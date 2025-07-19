cd fyp24-container

conda run -n fyp24-container --no-capture-output \
    fastapi run app.py --port 6724 --root-path /fyp24

# Equivalent to:
# conda activate fyp24-container
# fastapi run app.py --port 6724 --root-path /fyp24
