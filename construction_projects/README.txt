9 Feb 2026.

The workflow to create the Construction Area Polygons involves:

1) downloading the excel file from share point. To do this you must open the excel and save a copy to your downloads folder. I overwrite "C:\Users\jdsegars\Downloads\Facilities Project List.xlsx"

2) Using ArcGIS pro, I open my Construction_Projects.aprx. I click the Analysis tab and then look for Excel to Table and populate it:
Input Excel File = C:\Users\jdsegars\Downloads\Facilities Project List.xlsx
Output Table = C:\Users\jdsegars\Documents\ArcGIS\Projects\Construction_Projects\Construction_Projects.gdb\FacilitiesProjectList_ExcelToTable
Sheet Or Named Range = FN - Active
Row To Use As Field Names = 1
Cell Range = A1:M100
3) Run the process and then close ArcGIS pro.
4) open: "C:\Users\jdsegars\Documents\ArcGIS\Projects\Construction_Projects\Scripts\Create_Construction_Area_Polygons.py"
5) run the module
6) Open ArcGIS pro and verify then overwrite web layer 'construction project areas' in the Public folder.

https://experience.arcgis.com/experience/7b063270c2154678b98ea2b397584a0d


NOTE --> IF NEW BUILDINGS ARE ADDED YOU MUST EXPORT ANOTHER BLDGS.CSV.