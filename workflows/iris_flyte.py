# from sklearn.linear_model import LogisticRegression
from flytekit import task, workflow, Resources, ImageSpec, Secret
from flytekit.types.pickle import FlytePickle
# import pandas as pd
# import numpy as np


sklearn_image_spec = ImageSpec(
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.12.2",
    packages=["scikit-learn","pandas","numpy"],
    registry="localhost:30000",
)
if sklearn_image_spec.is_container():
    from sklearn.linear_model import LogisticRegression
    import pandas as pd
    import numpy as np
#@task decorators define the building blocks of your pipeline
@task(container_image=sklearn_image_spec,limits=Resources(mem="200Mi"))
def get_data() -> pd.DataFrame:
    
        
    df = pd.read_csv("https://raw.githubusercontent.com/TripathiAshutosh/dataset/main/iris.csv")
    return df

@task(container_image=sklearn_image_spec,limits=Resources(mem="200Mi"))
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    
    
    df = data.dropna()
    return df
@task(limits=Resources(mem="200Mi"))
def TrainTestSplit(data: pd.DataFrame) -> pd.DataFrame:
    # if sklearn_image_spec.is_container():
    #     import pandas as pd
    #     import numpy as np
    #     from sklearn.model_selection import train_test_split
    final_data = df
    target_column = 'class'
    X = final_data.loc[:,final_data.columns != target_column]
    y = final_data.loc[:,final_data.columns==target_column]
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,stratify = y,random_state = 47)
    print("training data")
    print("/n")
    print(X_train)
    print("test data")
    print("/n")
    print(X_test)
@task(container_image=sklearn_image_spec,limits=Resources(mem="200Mi"))
def train_model(data: pd.DataFrame) -> FlytePickle:
    """Train a model on the wine dataset."""
    features = data.drop("class", axis="columns")
    target = data["class"]
    return LogisticRegression(max_iter=1000).fit(features, target)
@workflow
def training_workflow() -> FlytePickle:
    """Put all of the steps together into a single workflow."""
    data = get_data()
    processed_data = process_data(data=data)
    return train_model(data=processed_data)
if __name__ == "__main__":
    # You can run this script with pre-defined arguments with `python flyte_workflow.py`
    # but we recommend running it with the `pyflyte run` CLI command, as you'll see in
    # the next step of this walkthrough.
    print(f"Running training_workflow() {training_workflow()}")