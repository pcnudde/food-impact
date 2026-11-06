mkdir -p output
mkdir -p input
cp host/input.csv input.csv

case "${JOB_TYPE:-impacts}" in
  stars|aia)
    # Add certification dropdowns (stars = AASHE STARS, aia = Anchors in Action). The worksheet
    # is emailed back for the user to fill in and upload at index.html.
    if [ "$JOB_TYPE" = "stars" ]; then PREP=1; else PREP=2; fi
    if papermill add_certifier_dropdowns.ipynb output/AddDropdownsOut.ipynb -p PREP_TYPE $PREP 2> papermill.log; then
      cp output/worksheet_dropdowns.xlsx "host/worksheet_${JOB_TYPE}_dropdowns.xlsx"
      python dropdown_email.py ok > host/email_body.txt
    else
      python dropdown_email.py failed papermill.log > host/email_body.txt
    fi
    cat papermill.log
    ;;
  *)
    cp host/input.csv output/input.csv

    # Run notebook
    papermill FoodImpacts.ipynb output/FoodImpactsOut.ipynb

    zip -r output.zip output
    cp output.zip host/output.zip
    ;;
esac
