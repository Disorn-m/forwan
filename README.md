# mm-asa-toolbox

Pre-requisite 
  Python 3.9-3.11
  Required modules (batch install file https://github.com/mottmac-global/mm-asa-toolbox-solar/blob/main/pip%20python%20module%20batch%20install.bat)
  
Steps to run streamlit
  1. Modify the "batch.bat" file in /project_contents/app/ by adding "cd" to you local path "C:\\....\project_contents\app\" to the line before "streamlit run
  MM_ASA_Toolbox.py --server.port 5998" e.g. "cd C:\Users\%USER%\OneDrive - Mott MacDonald\repos\mm_asa_toolbox\project_contents\app"
  
  2. run the "batch.bat" file

 
Steps to modify or create new tools
New tools should be uploaded to a branch or fork then create a pull request for final approval.
  1. Tools or pages are in /project_contents/app/pages/ each .py will represent one page
  2. streamlit API can be found https://docs.streamlit.io/library/api-reference
  3. update "environment.yml" to reflect the required modules
 
For further information regarding changes to deployment or any other questions please contact Fabien Blanchais or Disorn Maneewongvatana
