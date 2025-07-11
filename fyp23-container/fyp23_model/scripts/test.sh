# To run this script, please do it in the back-end folder:
# cd back-end/
# sh scripts/test.sh

# Clean up
echo "Clean up"
rm -rf ./scripts/outputs/
mkdir -p ./scripts/outputs/
chmod 777 ./scripts/outputs/

echo "----------------------------------"
echo "Test font2img.py with Chinese characters"
echo "----------------------------------"
mkdir -p ./scripts/outputs/content_folder
echo "測試" > ./scripts/outputs/char-input.txt
chmod 777 ./scripts/outputs/char-input.txt
python font2img.py \
    --ttf_path ./ttf_folder/PMingLiU.ttf \
    --save_path ./scripts/outputs/content_folder \
    --text_path ./scripts/outputs/char-input.txt
echo "----------------------------------"
echo "Expected output: 0 characters are missing in this font"
echo "Expected: Images are saved in ./scripts/outputs/content_folder"
echo "----------------------------------"

echo "----------------------------------"
echo "Test sample.py with the generated Chinese characters"
echo "----------------------------------"
mkdir -p ./scripts/outputs/results_web
mpiexec -n 1 python sample.py \
    --cfg_path ./cfg/test_cfg.yaml \
    --model_path ./ckpt/ema_0.9999_446000.pt \
    --sty_img_path ./lan.png \
    --con_folder_path ./scripts/outputs/content_folder \
    --total_txt_file ./wordlist.txt \
    --img_save_path ./scripts/outputs/results_web
echo "----------------------------------"
echo "Expected output: sampling complete"
echo "Expected: Images are saved in ./scripts/outputs/results_web"
echo "----------------------------------"

echo "----------------------------------"
echo "Test font2img.py with English and numerical characters"
echo "----------------------------------"
mkdir -p ./scripts/outputs/non_chinese
echo "Abc 123" > ./scripts/outputs/non-chinese.txt
chmod 777 ./scripts/outputs/non-chinese.txt
python font2img.py \
    --ttf_path ./ttf_folder/PMingLiU.ttf \
    --save_path ./scripts/outputs/non_chinese \
    --text_path ./scripts/outputs/non-chinese.txt
echo "----------------------------------"
echo "Expected output: n characters are missing in this font"
echo "(n = number of space characters in the input)"
echo "Note: It is normal that space characters are missing in the font"
echo "Expected: Images are saved in ./scripts/outputs/non_chinese"
echo "----------------------------------"
