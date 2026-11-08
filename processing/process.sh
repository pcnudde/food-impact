mkdir -p output
mkdir -p input
cp host/input.csv input.csv

# Result file names, set by the workflow from the uploaded worksheet's name (BASE_NAME is read by
# FoodImpacts.ipynb); without a name, results are named as before
ZIP_NAME="${ZIP_NAME:-output.zip}"
DROPDOWN_NAME="${DROPDOWN_NAME:-worksheet_${JOB_TYPE}_dropdowns.xlsx}"

case "${JOB_TYPE:-impacts}" in
  stars|aia)
    # Add certification dropdowns (stars = AASHE STARS, aia = Anchors in Action). The worksheet
    # is emailed back for the user to fill in and upload at index.html.
    if [ "$JOB_TYPE" = "stars" ]; then PREP=1; else PREP=2; fi
    if papermill add_certifier_dropdowns.ipynb output/AddDropdownsOut.ipynb -p PREP_TYPE $PREP 2> papermill.log; then
      cp output/worksheet_dropdowns.xlsx "host/$DROPDOWN_NAME"
      python dropdown_email.py ok > host/email_body.txt
    else
      python dropdown_email.py failed papermill.log > host/email_body.txt
    fi
    cat papermill.log
    ;;
  *)
    # The uploaded worksheet is not copied into the results zip (the user already has it)

    # Run notebook
    papermill FoodImpacts.ipynb output/FoodImpactsOut.ipynb

    zip -r "$ZIP_NAME" output
    cp "$ZIP_NAME" "host/$ZIP_NAME"
    ;;
esac
