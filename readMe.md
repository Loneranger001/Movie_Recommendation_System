- Steps to ready the application for Azure deployment
    - pip freeze requirements.txt for non-conda evns 
    - for conda envs
        - conda activate "env_name"
        - conda env export --no-builds > environment.yml
        - convert this yaml to requirements.txt 
    - Install gunicorn using pip install gunicorn
        - gunicorn --bind 0.0.0.0:$PORT app:app (On Unix like OS)
    - Install waitress using pip install waitress
        - export PORT=8000
        - export APP_DIR="/c/Users/alaskar/Documents/DataCamp/repository/DataScience101/portfolio-projects/Movie_Recommendation_System/data"
        - export MOVIE_PATH="ml-25m/movies.csv"
        - export RATINGS_PATH="ml-25m/ratings.csv"
        - waitress-serve --port=$PORT app:app (on Windows)\
    
    - Deploy yo Azure
        - az login
        - az appservice plan create --name myAppServicePlan --resource-group rgazapp01 --sku FREE
        - az webapp create --resource-group rgazapp01 --plan myAppServicePlan --name portfolio01webapp --runtime "PYTHON|3.8"
        - az webapp up --name portfolio01webapp --resource-group rgazapp01 --plan myAppServicePlan

    - Application log stream(for any issue)
        - az webapp log tail --name az900webapp01 --resource-group appsvc_linux_centralus

log stream 
az webapp deployment source config-zip --resource-group appsvc_linux_centralus --name az900webapp01 --src app-deployment.zip

conda create --name az900webapp01 --no-default-packages python=3.12
conda create --name leanpy312 --no-default-packages python=3.12 