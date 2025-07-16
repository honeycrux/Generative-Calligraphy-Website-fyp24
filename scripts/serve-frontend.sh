cd frontend

conda run -n generative-calligraphy-website --no-capture-output \
    fastapi run serve_frontend.py --port 6700

# Equivalent to:
# conda activate generative-calligraphy-website
# fastapi run serve_frontend.py --port 6700
