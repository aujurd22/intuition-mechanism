# SPOTS-10 Dataset
The SPOTS-10 dataset was created to evaluate machine learning algorithms. This dataset consists of a comprehensive collection of grayscale images showcasing the diverse patterns found in ten animal species. Specifically, SPOTS-10 features 32 × 32 grayscale images of 50,000 distinct markings of ten animals species. The dataset is divided into ten categories, with 5,000 images per category. The training set comprises 40,000 images, while the test
set contains 10,000 images. 

Below are samples taken from the SPOTS-10 dataset were each row represents a category in the dataset and columns, variations of the samples in that category.

![Samples from complete dataset](images/complete_dataset.png)

# Getting the Dataset
You can get the SPOTS-10 dataset by cloning this GitHub repository; the dataset appears under /dataset. This repo also contains some scripts for benchmark and the utilities folder that contains the files we used for making the MNIST-like dataset for SPOTS-10. You can also find some scripts that will help you load the train and test dataset and labels into a numpy array for training your benchmark model.

    git clone git@github.com:Amotica/SPOTS-10.git 

# Categories (Labels)
Each training and test samples is assigned to one of the following categories/labels:

| Label ID	| Category |
| ----- | ----------- |
| 0	| Cheetah |
| 1	| Deer |
| 2	| Giraffe |
| 3	| Hyena |
| 4	| Jaguar |
| 5	| Leopard |
| 6	| Tapir Calf |
| 7	| Tiger |
| 8	| Whale Shark |
| 9	| Zebra |

# Usage

Loading data with Python (requires numpy, struct and gzip)
Use utilities/spot-10-reader.py in this repo:
        
        import SPOT10Loader
        X_train, y_train = SPOT10Loader.get_data(kind="Train")
        X_test, y_test = SPOT10Loader.get_data(kind="Test")

# Citing SPOTS-10 Dataset
If you use SPOTS-10 in a publication, we would appreciate references to the following paper:

SPOTS-10: Animal Pattern Benchmark Dataset for Machine Learning Algorithms. [arXiv:2410.21044](https://arxiv.org/abs/2410.21044)

**Biblatex entry:**

    @online{
        2410.21044,
        Author = {John Atanbori},
        Title = {SPOTS-10: Animal Pattern Benchmark Dataset for Machine Learning Algorithms},
        Year = {2024},
        Eprint = {2410.21044},
        Eprinttype = {arXiv},
    }

**BibTex entry:**

    @misc{
        2410.21044,
        Author = {John Atanbori},
        Title = {SPOTS-10: Animal Pattern Benchmark Dataset for Machine Learning Algorithms},
        Year = {2024},
        Eprint = {arXiv:2410.21044},
    }
