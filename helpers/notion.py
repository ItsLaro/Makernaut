import os
from notion_client import Client
from sentence_transformers import SentenceTransformer, util

class NotionDB:

    def __init__(self):
        self.notion = Client(auth=str({os.environ["NOTION_CLIENT_ID"]}))
        # id for notion page with database containing FAQs
        self.faq_db_id = os.environ["NOTION_FAQ_DB_ID"]

        self.anc_cache = {}
        self.faq_cache = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # extracts text from notion db cell (supporting various text types)
    def extract_text(self, val):
        if val["type"] == "title":
            title_list = val.get("title", [])
            return title_list[0].get("plain_text", "") if title_list else ""
        
        elif val["type"] == "rich_text":
            rt_list = val.get("rich_text", [])
            return rt_list[0].get("plain_text", "") if rt_list else ""
        
        elif val["type"] == "text":
            return val.get("text", {}).get("content", "")
        
        else:
            return ""

    # internal "private" (i hate python) method used to retrieve all rows of the db
    def get_db_rows(self, db_name: str):

        # Map db_name to database_id
        db_map = {
            "qa_db": self.faq_db_id,
            "anc_db": "YOUR_ANC_DB_ID_HERE"
        }

        database_id = db_map.get(db_name.lower())

        if not database_id:
            print(f"Unknown database name: {db_name}")
            return []

        try:
            res = self.notion.databases.query(database_id=database_id)
            rows = res.get("results", [])
            extracted_text = []

            if not rows:
                print(f"No rows found in the {db_name} database.")

            else:
                for row in rows:
                    props = row.get("properties", {})
                    # Get the first two columns by insertion order
                    col_items = list(props.items())

                    first_col_name, first_col_val = col_items[0]
                    second_col_name, second_col_val = col_items[1]

                    first_val = self.extract_text(first_col_val)
                    second_val = self.extract_text(second_col_val)

                    extracted_text.append({
                        first_col_name: first_val,
                        second_col_name: second_val
                    })

                # print(f"\nAll rows from {db_name} as JSON:")
                # print(json.dumps(extracted_text, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"Failed to read {db_name} database:", e)
            extracted_text = []

        return extracted_text
    

    # add functionality for user to accept answer as right, if it is then add the question and answer to the cache
    def search_faq(self, user_question):

        if user_question not in self.faq_cache:
            try:
                db_rows = self.get_db_rows("qa_db")
                highest_match_score = 0
                ans = None

                for qa in db_rows:
                    # get the keys for question and answer
                    keys = list(qa.keys())
                    db_question = qa[keys[1]]
                    db_answer = qa[keys[0]]

                    question_match_score = self.questions_match(user_question, db_question)

                    # if question is >= 70% match compare it to the highest
                    # match so far, return the answer of the question w/ the 
                    # highest similarity  
                    if question_match_score >= 70 and question_match_score > highest_match_score:
                        ans = db_answer
                        highest_match_score = question_match_score

                return ans

            except Exception as e:
                print(e)
                return None
        else:
            return self.faq_cache[user_question]
    

    def questions_match(self, user_question: str, db_question: str):
        # cosine similarity to compare closeness of two strings
        emb1 = self.model.encode(user_question, convert_to_tensor=True)
        emb2 = self.model.encode(db_question, convert_to_tensor=True)
        similarity = util.cos_sim(emb1, emb2).item()
        return similarity * 100 