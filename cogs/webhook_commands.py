import os
import re
import json
import time
import hmac
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import discord
from discord.ext import commands
import config

# Channel IDs for webhook commands
WEBHOOK_CHANNEL_ID = 0 if config.isProd else 1277118187439263895

# Allowed webhook IDs
ALLOWED_WEBHOOK_IDS = [] if config.isProd else ["1415136852570017812"]

# Webhook configuration  
WEBHOOK_RATE_LIMIT_PER_MINUTE = 30
COMMAND_PREFIX = 'BOT_CMD:'
TIMESTAMP_WINDOW_SECONDS = 300  # 5 minutes


class WebhookCommands(commands.Cog):
    """
    Webhook command handler that listens for webhook messages in designated channels
    and executes bot commands based on parsed patterns with mandatory HMAC validation.
    
    USAGE:
    ------
    All webhook messages must follow this format:
    BOT_CMD:<REQUEST_ID>:<COMMAND>:<PARAM1>:<PARAM2>:<TIMESTAMP>:<HMAC_SIGNATURE>
    
    Example:
    BOT_CMD:req001:ASSIGN_ROLE:123456789:987654321:1640995200:a1b2c3d4e5f6...
    
    HMAC SIGNATURE GENERATION:
    -------------------------
    1. Build message without signature: "BOT_CMD:req001:ASSIGN_ROLE:123456789:987654321:1640995200"
    2. Generate HMAC-SHA256: hmac(WEBHOOK_SECRET_KEY, message)
    3. Append signature: message + ":" + signature
    
    SUPPORTED COMMANDS:
    ------------------
    ASSIGN_ROLE:user_id:role_id     - Assign role to user
    REMOVE_ROLE:user_id:role_id     - Remove role from user  
    SEND_MESSAGE:channel_id:content - Send message to channel
    GET_USER_INFO:user_id           - Get user information
    
    SECURITY:
    --------
    - HMAC validation is mandatory (WEBHOOK_SECRET_KEY required)
    - 5-minute timestamp window to prevent replay attacks
    - Rate limiting: 30 commands per minute per webhook
    - Only allowed webhook IDs can send commands
    
    RESPONSES:
    ---------
    Success: [OK] BOT_RESPONSE:<REQUEST_ID>:SUCCESS:<COMMAND>:<RESULT_DATA>
    Error:   [ERR] BOT_RESPONSE:<REQUEST_ID>:ERROR:<COMMAND>:<ERROR_CODE>:<ERROR_MESSAGE>
    HMAC:    [ERR] HMAC_VALIDATION_FAILED: <ERROR_DETAILS>
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Configuration
        self.webhook_channel_id = WEBHOOK_CHANNEL_ID
        self.allowed_webhook_ids = ALLOWED_WEBHOOK_IDS
        self.rate_limit_per_minute = WEBHOOK_RATE_LIMIT_PER_MINUTE
        self.command_prefix = COMMAND_PREFIX
        
        # HMAC validation (mandatory)
        self.webhook_secret = os.getenv('WEBHOOK_SECRET_KEY', '').strip()
        
        if not self.webhook_secret:
            raise ValueError("WEBHOOK_SECRET_KEY is required in environment variables for secure webhook validation")
        
        # Rate limiting storage: webhook_id -> list of timestamps
        self.rate_limiter: Dict[str, List[float]] = {}
        
        # Command definitions with parameters and required permissions
        self.webhook_commands = {
            'ASSIGN_ROLE': {'params': ['user_id', 'role_id'], 'permissions': ['manage_roles']},
            'REMOVE_ROLE': {'params': ['user_id', 'role_id'], 'permissions': ['manage_roles']},
            'SEND_MESSAGE': {'params': ['channel_id', 'message_content'], 'permissions': ['send_messages']},
            'SEND_DM': {'params': ['user_id', 'message_content'], 'permissions': ['send_messages']},
            'CREATE_ROLE': {'params': ['role_name', 'color', 'permissions'], 'permissions': ['manage_roles']},
            'DELETE_MESSAGE': {'params': ['channel_id', 'message_id'], 'permissions': ['manage_messages']},
            'BAN_USER': {'params': ['user_id', 'reason'], 'permissions': ['ban_members']},
            'KICK_USER': {'params': ['user_id', 'reason'], 'permissions': ['kick_members']},
            'GET_USER_INFO': {'params': ['user_id'], 'permissions': []},
            'GET_CHANNEL_INFO': {'params': ['channel_id'], 'permissions': []},
            'LIST_ROLES': {'params': [], 'permissions': []},
        }
    
    def _is_rate_limited(self, webhook_id: str) -> bool:
        """Check if webhook is rate limited"""
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old timestamps
        if webhook_id not in self.rate_limiter:
            self.rate_limiter[webhook_id] = []
        
        # Remove timestamps older than 1 minute
        self.rate_limiter[webhook_id] = [
            timestamp for timestamp in self.rate_limiter[webhook_id] 
            if timestamp > minute_ago
        ]
        
        # Check if under rate limit
        if len(self.rate_limiter[webhook_id]) >= self.rate_limit_per_minute:
            return True
        
        # Add current timestamp
        self.rate_limiter[webhook_id].append(now)
        return False
    
    def _validate_hmac_signature(self, content: str) -> Tuple[bool, str]:
        """
        Validate HMAC signature in webhook message (mandatory)
        Returns: (is_valid, error_message)
        """
        if not content.startswith(self.command_prefix):
            return False, "Invalid command prefix"
        
        # Remove prefix and split by colon
        command_part = content[len(self.command_prefix):]
        parts = command_part.split(':')
        
        if len(parts) < 4:  # Need at least: req_id:command:timestamp:signature
            return False, "Missing HMAC signature - all webhook messages must include timestamp and signature"
        
        # Extract signature and timestamp (last two parts)
        signature = parts[-1]
        timestamp_str = parts[-2]
        message_without_signature = content[:content.rfind(':' + signature)]
        
        # Validate timestamp format and freshness (prevent replay attacks)
        try:
            msg_timestamp = int(timestamp_str)
            current_time = int(time.time())
            time_diff = abs(current_time - msg_timestamp)
            
            if time_diff > TIMESTAMP_WINDOW_SECONDS:
                return False, f"Message timestamp too old ({time_diff} seconds)"
                
        except ValueError:
            return False, "Invalid timestamp format"
        
        # Verify HMAC signature
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                message_without_signature.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid HMAC signature"
                
            return True, ""
            
        except Exception as e:
            return False, f"HMAC validation error: {str(e)}"
    
    def _parse_command(self, content: str) -> Optional[Dict[str, str]]:
        """
        Parse webhook command from message content
        Expected format without HMAC: BOT_CMD:<REQUEST_ID>:<COMMAND>:<PARAM1>:<PARAM2>:...
        Expected format with HMAC: BOT_CMD:<REQUEST_ID>:<COMMAND>:<PARAM1>:<PARAM2>:<TIMESTAMP>:<SIGNATURE>
        """
        # Validate HMAC signature first
        is_valid, error_msg = self._validate_hmac_signature(content)
        if not is_valid:
            print(f"HMAC validation failed: {error_msg}")
            return None
        
        if not content.startswith(self.command_prefix):
            return None
        
        # Remove prefix and split by colon
        command_part = content[len(self.command_prefix):]
        parts = command_part.split(':')
        
        # Remove HMAC signature and timestamp (mandatory)
        if len(parts) >= 4:
            # Remove timestamp and signature from parsing
            parts = parts[:-2]
        
        if len(parts) < 2:  # Need at least REQUEST_ID, COMMAND
            return None
        
        request_id = parts[0]
        command = parts[1].upper()
        params = parts[2:] if len(parts) > 2 else []
        
        # Validate command exists
        if command not in self.webhook_commands:
            return None
        
        return {
            'request_id': request_id,
            'command': command,
            'params': params
        }
    
    def _validate_webhook_message(self, message: discord.Message) -> bool:
        """Validate that message is from an allowed webhook"""
        # Check if message is in the correct channel
        if message.channel.id != self.webhook_channel_id:
            return False
        
        # Check if message is from a webhook
        if not message.webhook_id:
            return False
        
        # Check if webhook ID is in allowed list
        webhook_id_str = str(message.webhook_id)
        if webhook_id_str not in self.allowed_webhook_ids:
            return False
        
        return True
    
    async def _send_response(self, channel: discord.TextChannel, request_id: str, 
                           command: str, success: bool, result_data: str = "", 
                           error_code: str = "", error_message: str = ""):
        """Send formatted response back to webhook channel"""
        if success:
            response = f"[OK] BOT_RESPONSE:{request_id}:SUCCESS:{command}:{result_data}"
        else:
            response = f"[ERR] BOT_RESPONSE:{request_id}:ERROR:{command}:{error_code}:{error_message}"
        
        try:
            await channel.send(response)
        except Exception as e:
            print(f"Failed to send webhook response: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for webhook messages and process commands"""
        # Skip if not a valid webhook message
        if not self._validate_webhook_message(message):
            return
        
        # Validate HMAC first for better error reporting
        is_hmac_valid, hmac_error = self._validate_hmac_signature(message.content)
        if not is_hmac_valid:
            # Send HMAC validation error back to webhook channel
            await message.channel.send(f"[ERR] HMAC_VALIDATION_FAILED: {hmac_error}")
            return
        
        # Parse command
        parsed = self._parse_command(message.content)
        if not parsed:
            return
        
        request_id = parsed['request_id']
        command = parsed['command']
        params = parsed['params']
        
        # Check rate limiting
        webhook_id = str(message.webhook_id)
        if self._is_rate_limited(webhook_id):
            await self._send_response(
                message.channel, request_id, command, False,
                error_code="RATE_LIMITED",
                error_message="Webhook rate limit exceeded"
            )
            return
        
        # Execute command with timeout
        try:
            await asyncio.wait_for(
                self._execute_command(message.channel, request_id, command, params),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            await self._send_response(
                message.channel, request_id, command, False,
                error_code="TIMEOUT",
                error_message="Command execution timed out"
            )
        except Exception as e:
            await self._send_response(
                message.channel, request_id, command, False,
                error_code="INTERNAL_ERROR",
                error_message=f"Internal error: {str(e)}"
            )
            print(f"Webhook command error: {e}")
    
    async def _execute_command(self, channel: discord.TextChannel, request_id: str, 
                             command: str, params: List[str]):
        """Execute the parsed webhook command"""
        command_info = self.webhook_commands[command]
        expected_params = command_info['params']
        
        # Validate parameter count
        if len(params) != len(expected_params):
            await self._send_response(
                channel, request_id, command, False,
                error_code="INVALID_PARAMS",
                error_message=f"Expected {len(expected_params)} parameters, got {len(params)}"
            )
            return
        
        # Route to appropriate command handler
        if command == 'ASSIGN_ROLE':
            await self._handle_assign_role(channel, request_id, params)
        elif command == 'REMOVE_ROLE':
            await self._handle_remove_role(channel, request_id, params)
        elif command == 'SEND_MESSAGE':
            await self._handle_send_message(channel, request_id, params)
        elif command == 'GET_USER_INFO':
            await self._handle_get_user_info(channel, request_id, params)
        else:
            # Command not implemented yet
            await self._send_response(
                channel, request_id, command, False,
                error_code="NOT_IMPLEMENTED",
                error_message=f"Command {command} not implemented yet"
            )
    
    async def _handle_assign_role(self, channel: discord.TextChannel, request_id: str, params: List[str]):
        """Handle ASSIGN_ROLE command"""
        user_id_str, role_id_str = params
        
        try:
            user_id = int(user_id_str)
            role_id = int(role_id_str)
            guild = channel.guild
            
            # Get user and role
            user = guild.get_member(user_id)
            if not user:
                await self._send_response(
                    channel, request_id, 'ASSIGN_ROLE', False,
                    error_code="USER_NOT_FOUND",
                    error_message=f"User {user_id} not found in guild"
                )
                return
            
            role = guild.get_role(role_id)
            if not role:
                await self._send_response(
                    channel, request_id, 'ASSIGN_ROLE', False,
                    error_code="ROLE_NOT_FOUND",
                    error_message=f"Role ID {role_id} not found"
                )
                return
            
            # Check if user already has role
            if role in user.roles:
                await self._send_response(
                    channel, request_id, 'ASSIGN_ROLE', True,
                    result_data=f"User {user.display_name} already has role {role.name}"
                )
                return
            
            # Assign role
            await user.add_roles(role, reason=f"Webhook command (Request: {request_id})")
            
            await self._send_response(
                channel, request_id, 'ASSIGN_ROLE', True,
                result_data=f"Role {role.name} assigned to {user.display_name}"
            )
            
        except ValueError as e:
            if "user_id" in str(e) or user_id_str in str(e):
                error_msg = "User ID must be a valid integer"
            else:
                error_msg = "Role ID must be a valid integer"
            await self._send_response(
                channel, request_id, 'ASSIGN_ROLE', False,
                error_code="INVALID_ID",
                error_message=error_msg
            )
        except discord.Forbidden:
            await self._send_response(
                channel, request_id, 'ASSIGN_ROLE', False,
                error_code="PERMISSION_DENIED",
                error_message="Bot lacks permission to assign roles"
            )
        except Exception as e:
            await self._send_response(
                channel, request_id, 'ASSIGN_ROLE', False,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
    
    async def _handle_remove_role(self, channel: discord.TextChannel, request_id: str, params: List[str]):
        """Handle REMOVE_ROLE command"""
        user_id_str, role_id_str = params
        
        try:
            user_id = int(user_id_str)
            role_id = int(role_id_str)
            guild = channel.guild
            
            # Get user and role
            user = guild.get_member(user_id)
            if not user:
                await self._send_response(
                    channel, request_id, 'REMOVE_ROLE', False,
                    error_code="USER_NOT_FOUND",
                    error_message=f"User {user_id} not found in guild"
                )
                return
            
            role = guild.get_role(role_id)
            if not role:
                await self._send_response(
                    channel, request_id, 'REMOVE_ROLE', False,
                    error_code="ROLE_NOT_FOUND",
                    error_message=f"Role ID {role_id} not found"
                )
                return
            
            # Check if user doesn't have the role
            if role not in user.roles:
                await self._send_response(
                    channel, request_id, 'REMOVE_ROLE', True,
                    result_data=f"User {user.display_name} does not have role {role.name}"
                )
                return
            
            # Remove role
            await user.remove_roles(role, reason=f"Webhook command (Request: {request_id})")
            
            await self._send_response(
                channel, request_id, 'REMOVE_ROLE', True,
                result_data=f"Role {role.name} removed from {user.display_name}"
            )
            
        except ValueError as e:
            if "user_id" in str(e) or user_id_str in str(e):
                error_msg = "User ID must be a valid integer"
            else:
                error_msg = "Role ID must be a valid integer"
            await self._send_response(
                channel, request_id, 'REMOVE_ROLE', False,
                error_code="INVALID_ID",
                error_message=error_msg
            )
        except discord.Forbidden:
            await self._send_response(
                channel, request_id, 'REMOVE_ROLE', False,
                error_code="PERMISSION_DENIED",
                error_message="Bot lacks permission to remove roles"
            )
        except Exception as e:
            await self._send_response(
                channel, request_id, 'REMOVE_ROLE', False,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
    
    async def _handle_send_message(self, channel: discord.TextChannel, request_id: str, params: List[str]):
        """Handle SEND_MESSAGE command"""
        channel_id_str, message_content = params
        
        try:
            channel_id = int(channel_id_str)
            target_channel = self.bot.get_channel(channel_id)
            
            if not target_channel:
                await self._send_response(
                    channel, request_id, 'SEND_MESSAGE', False,
                    error_code="CHANNEL_NOT_FOUND",
                    error_message=f"Channel {channel_id} not found"
                )
                return
            
            # Send message
            sent_message = await target_channel.send(message_content)
            
            await self._send_response(
                channel, request_id, 'SEND_MESSAGE', True,
                result_data=f"Message sent to #{target_channel.name} (ID: {sent_message.id})"
            )
            
        except ValueError:
            await self._send_response(
                channel, request_id, 'SEND_MESSAGE', False,
                error_code="INVALID_CHANNEL_ID",
                error_message="Channel ID must be a valid integer"
            )
        except discord.Forbidden:
            await self._send_response(
                channel, request_id, 'SEND_MESSAGE', False,
                error_code="PERMISSION_DENIED",
                error_message="Bot lacks permission to send messages to target channel"
            )
        except Exception as e:
            await self._send_response(
                channel, request_id, 'SEND_MESSAGE', False,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
    
    async def _handle_get_user_info(self, channel: discord.TextChannel, request_id: str, params: List[str]):
        """Handle GET_USER_INFO command"""
        user_id_str = params[0]
        
        try:
            user_id = int(user_id_str)
            guild = channel.guild
            
            # Get user
            user = guild.get_member(user_id)
            if not user:
                await self._send_response(
                    channel, request_id, 'GET_USER_INFO', False,
                    error_code="USER_NOT_FOUND",
                    error_message=f"User {user_id} not found in guild"
                )
                return
            
            # Build user info
            user_info = {
                'id': user.id,
                'username': user.name,
                'display_name': user.display_name,
                'discriminator': user.discriminator,
                'avatar_url': str(user.avatar.url) if user.avatar else None,
                'joined_at': user.joined_at.isoformat() if user.joined_at else None,
                'created_at': user.created_at.isoformat(),
                'roles': [role.name for role in user.roles if role.name != '@everyone'],
                'status': str(user.status),
                'is_bot': user.bot
            }
            
            # Convert to JSON string for response
            result_json = json.dumps(user_info, separators=(',', ':'))
            
            await self._send_response(
                channel, request_id, 'GET_USER_INFO', True,
                result_data=result_json
            )
            
        except ValueError:
            await self._send_response(
                channel, request_id, 'GET_USER_INFO', False,
                error_code="INVALID_USER_ID",
                error_message="User ID must be a valid integer"
            )
        except Exception as e:
            await self._send_response(
                channel, request_id, 'GET_USER_INFO', False,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )


async def setup(bot):
    await bot.add_cog(WebhookCommands(bot))
