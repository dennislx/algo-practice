import collections
import glob
import json
import os
from typing import Dict

import requests
from requests.sessions import Session

USER_AGENT = os.getenv("USER_AGENT")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
BADGE_PREFIX = '<img src="https://img.shields.io/badge/'
BADGE_SUFFIX = '.svg?style=flat-square" />\n'


class ReadmeWriter:
  def __init__(self):
    self.session: Session = requests.Session()
    self.session.cookies["LEETCODE_SESSION"] = LEETCODE_SESSION
    self.res: Dict[str, object] = json.loads(self.session.get(
        "https://leetcode.com/api/problems/all",
        headers={"User-Agent": USER_AGENT, "Connection": "keep-alive"},
        timeout=10,
    ).content.decode("utf-8"))
    self.problems = self.res["stat_status_pairs"]
    self.problems.sort(key=lambda x: x["stat"]["frontend_question_id"])
    self.sols_path = "solutions/"

  def write_readme(self) -> None:
    """Update README.md by folder files"""
    num_total: int = self.res["num_total"]
    prob_count = collections.Counter()  # {int (level): int}
    ac_count = collections.Counter()  # {int (level): int}

    for problem in self.problems:
      # 1 := easy, 2 := medium, 3 := hard
      level: int = problem["difficulty"]["level"]
      prob_count[level] += 1
      frontend_question_id: int = problem["stat"]["frontend_question_id"]
      filled_num: int = str(frontend_question_id).zfill(4)
      match = glob.glob(f"{self.sols_path}{filled_num}*")
      if match:
        ac_count[level] += 1

    num_solved = sum(ac_count.values())

    solved_percentage: float = round((num_solved / num_total) * 100, 2)
    solved_badge: str = f"{BADGE_PREFIX}Solved-{num_solved}/{num_total}%20=%20{solved_percentage}%25-blue{BADGE_SUFFIX}"
    easy_badge: str = f"{BADGE_PREFIX}Easy-{ac_count[1]}/{prob_count[1]}-5CB85D{BADGE_SUFFIX}"
    medium_badge: str = f"{BADGE_PREFIX}Medium-{ac_count[2]}/{prob_count[2]}-F0AE4E{BADGE_SUFFIX}"
    hard_badge: str = f"{BADGE_PREFIX}Hard-{ac_count[3]}/{prob_count[3]}-D95450{BADGE_SUFFIX}"

    # Write to README
    with open("README.md", "r") as f:
      original_readme = f.readlines()

    # Find the line with solved badge and replace the following 4 lines
    for i, line in enumerate(original_readme):
      if line.startswith('<img src="https://img.shields.io/badge/Solved'):
        break

    original_readme[i] = solved_badge
    original_readme[i + 2] = easy_badge
    original_readme[i + 3] = medium_badge
    original_readme[i + 4] = hard_badge

    with open("README.md", "w+") as f:
      for line in original_readme:
        f.write(line)
