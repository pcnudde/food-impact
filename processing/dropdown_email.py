"""Prints the email text for a dropdown job (JOB_TYPE stars or aia). Used by process.sh.

    python dropdown_email.py ok                    -> instructions for the attached worksheet
    python dropdown_email.py failed papermill.log  -> why it failed, from the notebook's error
"""
import os
import re
import sys

SITE = "https://pcnudde.github.io/food-impact/"
job = os.environ.get("JOB_TYPE", "")
name = "AASHE STARS" if job == "stars" else "Anchors in Action"
page = f"{SITE}{job}.html"

if sys.argv[1:2] == ["ok"]:
    if job == "stars":
        steps = [
            "Open it in Excel or LibreOffice Calc.",
            "For each product, choose from the AASHE columns that apply (Organic, Animal Welfare, "
            "Environment, Labor, Small Producers, Seafood). Fill in every column that applies; "
            "a product is counted once toward the STARS share. The AASHE Lookup sheet lists the "
            "STARS categories each option meets.",
            "Optionally fill in Plant Based (y or 1-4) and Explanation. The Notes sheet explains them. "
            "Leave cells blank where nothing applies.",
        ]
    else:
        steps = [
            "Open it in Excel or LibreOffice Calc.",
            "For animal products, choose the AW food group first, then AW. Choose Env, Labor, "
            "Local (GFPP level) and Social Impact Supplier where they apply. The Notes sheet "
            "explains each column.",
            "In the first row only, choose Program year and Nutrition checklist points (%) "
            "(the last two columns).",
            "Optionally fill in Plant Based (y or 1-4) and Explanation. Leave cells blank where "
            "nothing applies.",
        ]
    steps += ["Save the file, keeping it as .xlsx.",
              f"Upload the saved file at {SITE} to get your food impact results with the {name} shares."]
    print(f"Attached is your worksheet with {name} certification dropdowns added.\n")
    for i, s in enumerate(steps, 1):
        print(f"{i}. {s}")
    sys.exit(0)

# Failed: find the notebook's error message in the papermill log
text = ""
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    with open(sys.argv[2], encoding="utf-8", errors="replace") as f:
        text = re.sub(r"\x1b\[[0-9;]*m", "", f.read())           # drop terminal colours
errors = re.findall(r"^(\w*(?:Error|Exception)): (.+)$", text, re.M)
error = errors[-1][1].strip() if errors else ""

print(f"Sorry, we could not add the {name} dropdowns to your worksheet.\n")
m = re.search(r"already has a column named '(.+?)'", error)
if m:
    print(f"Your worksheet already has a column named \"{m.group(1)}\", so it looks like it already "
          "has the dropdown columns. If you have filled them in, upload it at "
          f"{SITE} to get your results. Otherwise, upload the worksheet without those columns at {page}")
else:
    print("Please check that the file is a purchasing worksheet with its column headings in one row "
          f"above the items, and try again at {page}")
    if error:
        print(f"\nThe error was: {error}")
