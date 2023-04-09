import glob
import json
import logging
import os
from io import TextIOWrapper
from typing import Dict, List

import requests
from requests.adapters import Response
from requests.sessions import Session
from dotenv import load_dotenv

load_dotenv()

# from config.colors import colors
# from config.gsheet import sheet

USER_AGENT = os.getenv("USER_AGENT")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")

class MkdocsWriter:
  def __init__(self, argv: List[str]):
    # self.records: List[dict[str, str]] = sheet.get_all_records()
    self.session: Session = requests.Session()
    self.session.cookies["LEETCODE_SESSION"] = LEETCODE_SESSION
    self.res: Dict[str, object] = json.loads(self.session.get(
        "https://leetcode.com/api/problems/all",
        headers={"User-Agent": USER_AGENT, "Connection": "keep-alive"},
        timeout=10,
    ).content.decode("utf-8"))
    # fetch all solved problems list
    self.problems = [p for p in self.res["stat_status_pairs"] if p['status'] == 'ac'] 
    self.problems.sort(key=lambda x: x["stat"]["frontend_question_id"])
    self.finish_problem = {}

    if len(argv) == 2 and argv[1] == '--mock':
      self.problems = self.problems[:2]
      # self.records = self.records[:2]

    self.sols_path = "solutions/"
    self.problems_path = "mkdocs/docs/problems/"
    self.__create_problems_path_if_needed()

  def __create_problems_path_if_needed(self):
    try:
      os.mkdir(self.problems_path)
    except:
      pass

  def __get_problem_by_slug(self, slug: str) -> dict:
    url = "https://leetcode.com/graphql"
    params = {
        "operationName": "questionData",
        "variables": {"titleSlug": slug},
        "query": """
          query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
              title
              difficulty
              likes
              dislikes
              topicTags {
                name
              }
            }
          }
        """
    }

    json_data = json.dumps(params).encode("utf8")
    headers = {"User-Agent": USER_AGENT, "Connection":
               "keep-alive", "Content-Type": "application/json",
               "Referer": f"https://leetcode.com/problems/{slug}"}

    res: None or Response = None
    while not res:
      res = self.session.post(url, data=json_data, headers=headers, timeout=10)
    question: dict = res.json()
    return question["data"]["question"]

  def __write_code(
          self, f: TextIOWrapper, filled_num: str, problem_path: str,
          approach_index: int) -> None:
    for extension, lang, tab in [
        ("cpp", "cpp", "C++"),
        ("java", "java", "Java"),
        ("py", "python", "Python"),
        ("js", "javascript", "Javascript"),
    ]:
      suffix: str = "" if approach_index == 1 else f"-{approach_index}"
      code_file_dir = f"{problem_path}/{filled_num}{suffix}.{extension}"

      if not os.path.exists(code_file_dir):
        continue

      f.write(f'=== "{tab}"\n\n')
      with open(code_file_dir) as code_file:
        code = ["    " + line for line in code_file.readlines()]
        f.write(f"    ```{lang}\n")
        for line in code:
          f.write(line)
        f.write("\n")
        f.write("    ```")
        f.write("\n\n")

  def write_problems(self, finished_problems, LOCK) -> None:
    for problem in self.problems:
      frontend_question_id: int = problem["stat"]["frontend_question_id"]
      # Temporarily solve LeetCode API inconsistency.
      if frontend_question_id == 2890:
        frontend_question_id = 2590
      i: int = frontend_question_id - 1
      filled_num: str = str(i + 1).zfill(4)
      # Check if this problem is solved (has local file), skip if I haven't
      matches = glob.glob(f"{self.sols_path}{filled_num}*/readme.md")
      if not matches:
        continue
      with open(matches[0], 'r') as f:
        readme = f.read()
      title: str = problem['stat']['question__title']
      try:
        with LOCK:
          finished_problems[frontend_question_id] = title
      except Exception as e:
        print(e)
      print(f"Write {frontend_question_id}. {title}...")
      with open(f"{self.problems_path}{filled_num}.md", "w") as f:
          f.write(readme)
          f.write("\n\n")
          self.__write_code(f, filled_num, os.path.dirname(matches[0]), 1)

  def write_mkdocs(self, finished_problems) -> None:
    """Append nav titles to mkdocs.yml"""
    with open("mkdocs/mkdocs.yml", "a+") as f:
      f.write("  - Problems:\n")
      for problem_id, problem_title in finished_problems.items():
        f.write(f'      - "{problem_id}. {problem_title}": problems/{str(problem_id).zfill(4)}.md\n')
