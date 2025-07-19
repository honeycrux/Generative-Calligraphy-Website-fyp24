# frontend
conda env create -f frontend/environment.yml

# fyp23-container
conda env create -f fyp23-container/environment.yml

# fyp24-container
conda create -n fyp24-container python=3.9 -y
conda run -n fyp24-container --no-capture-output \
    pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
conda run -n fyp24-container --no-capture-output \
    pip install -r fyp24-container/requirements.txt
