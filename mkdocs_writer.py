import glob
import json
import logging
import os
from io import TextIOWrapper
from typing import Dict, List

import requests
from requests.adapters import Response
from requests.sessions import Session

from config.colors import colors
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

  def __get_display_title(
          self, *, problem_no: int, title: str, link: str, emoji: str) -> str:
    display_title: str = f"# [{problem_no}. {title}]({link})"
    if emoji:
      display_title += " " + emoji
    return display_title

  def __get_difficulty_color(self, difficulty: str) -> str:
    if difficulty == "Easy":
      return "00a690"
    if difficulty == "Medium":
      return "ffaf00"
    return "ff284b"

  def __get_tag_strings(self, *, problem_tags: List[str]) -> List[str]:
    tag_strings: List[str] = []
    for problem_tag in problem_tags:
      if problem_tag in colors:
        color: str = colors[problem_tag]
        tag_string: str = f"![](https://img.shields.io/badge/-{problem_tag.replace('-', '--')}-{color}.svg?style=flat-square)"
        tag_strings.append(tag_string)
    return tag_strings

  def __get_emoji(self, *, likes: int, dislikes: int) -> str:
    votes: int = likes + dislikes
    if votes == 0:
      return ""
    likes_percentage: float = likes / votes
    if likes_percentage > 0.8:
      return ":thumbsup:"
    if likes_percentage < 0.5:
      return ":thumbsdown:"
    return ""

  def __write_code(
          self, f: TextIOWrapper, filled_num: str, problem_path: str,
          approach_index: int) -> None:
    for extension, lang, tab in [
        ("cpp", "cpp", "C++"),
        ("java", "java", "Java"),
        ("py", "python", "Python"),
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
      matches = glob.glob(f"{self.sols_path}{filled_num}*")
      if not matches:
        continue

      slug: str = problem["stat"]["question__title_slug"]
      question = self.__get_problem_by_slug(slug)
      if question == None:
        logging.warn("question is None")
        logging.warn(f"{frontend_question_id = }")
        logging.warn(f"{slug = }")
        continue

      title: str = question["title"]
      try:
        with LOCK:
          finished_problems[frontend_question_id] = title
      except Exception as e:
        print(e)
      print(f"Write {frontend_question_id}. {title}...")
      difficulty: str = question["difficulty"]
      likes: int = question["likes"]
      dislikes: int = question["dislikes"]
      problem_tags: List[str] = []
      for tag in question["topicTags"]:
        problem_tags.append(tag["name"])
      link: str = f'https://leetcode.com/problems/{problem["stat"]["question__title_slug"]}'
      emoji: str = self.__get_emoji(likes=likes, dislikes=dislikes)
      # time_complexities: List[str] = self.records[i]["Time"].split("; ")
      # space_complexities: List[str] = self.records[i]["Space"].split("; ")
      # ways = self.records[i]["Ways"].split("; ")

      with open(f"{self.problems_path}{filled_num}.md", "w") as f:
        # Write the first line of the .md file
        # [No. display_title](link)
        display_title = self.__get_display_title(
            problem_no=i + 1, title=title, link=link, emoji=emoji)
        f.write(f"{display_title}\n\n")

        # Write the colorful difficulty string
        difficulty_color: str = self.__get_difficulty_color(difficulty)
        difficulty_string: str = f"![](https://img.shields.io/badge/-{difficulty}-{difficulty_color}.svg?style=for-the-badge)"
        f.write(difficulty_string)
        f.write("\n\n")

        # Write the colorful tags
        tag_strings = self.__get_tag_strings(problem_tags=problem_tags)
        f.write(f'{" ".join(tag_strings)}\n\n')

        ways, time_complexities, space_complexities = [], 0, 0
        if len(ways) > 1:
          # For each way to solve this problem
          approach_index = 1
          for way, time_complexity, space_complexity in zip(
                  ways, time_complexities, space_complexities):
            f.write(f"## Approach {approach_index}: {way}\n\n")
            f.write(f"- [x] **Time:** {time_complexity}\n")
            f.write(f"- [x] **Space:** {space_complexity}\n")
            f.write("\n")
            self.__write_code(f, filled_num, matches[0], approach_index)
            approach_index += 1
        else:
          if time_complexities:
            f.write(f"- [x] **Time:** {time_complexities[0]}\n")
          if space_complexities:
            f.write(f"- [x] **Space:** {space_complexities[0]}\n")
          f.write("\n")
          self.__write_code(f, filled_num, matches[0], 1)

  def write_mkdocs(self, finished_problems) -> None:
    """Append nav titles to mkdocs.yml"""
    with open("mkdocs/mkdocs.yml", "a+") as f:
      f.write("  - Problems:\n")
      for problem_id, problem_title in finished_problems.items():
        f.write(f'      - "{problem_id}. {problem_title}": problems/{str(problem_id).zfill(4)}.md\n')
