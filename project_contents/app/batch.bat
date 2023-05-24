#CONDA
cd C:\Users\BLA88076\OneDrive - Mott MacDonald\repos\mm-asa-toolbox\project_contents\app
cd C:\Users\sea90107\OneDrive - Mott MacDonald\repos\mm_asa_toolbox\project_contents\app
cd C:\Users\cape0\Documents\GitHub\mm-asa-toolbox\project_contents\app
streamlit run MM_ASA_Toolbox.py --server.port 5998


#DockerApp&cmd
cd C:\Users\BLA88076\OneDrive - Mott MacDonald\repos\mm-asa-toolbox
docker system prune --volumes --all
docker build -t mm_asa_toolbox:v1 .
	[1-7/15]ON
	[8-12/15]OFF
	[13-15/15]ON

----docker run --rm -p 8880:8501 mm_asa_toolbox:v1
----localhost:8880

az login
az acr create --name containertoolbox --resource-group resource_group_ASA --sku Basic
az acr login -n containertoolbox
docker build -t mm_asa_toolbox:v1 .
docker tag mm_asa_toolbox:v1 containertoolbox.azurecr.io/mm_asa_toolbox:v1
docker push containertoolbox.azurecr.io/mm_asa_toolbox:v1
az acr update -n containertoolbox --admin-enabled true
az acr credential show --name  containertoolbox
az container create --resource-group resource_group_ASA --name asatoolbox -f deployment.yml
