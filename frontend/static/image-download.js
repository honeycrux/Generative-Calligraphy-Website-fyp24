const format = "png"; // Default format for image download

function getTimestamp() {
    return new Date().valueOf();
}

function createCanvasDownloadHandler(imageName, suffix = "") {
    if (suffix != "" && !suffix.startsWith("-")) {
        suffix = `-${suffix}`;
    }

    return (canvas) => {
        // Convert the canvas to a data URL
        const dataURL = canvas.toDataURL(`image/${format}`);

        // Optionally, you can trigger a download for the modified image
        const link = document.createElement("a");
        link.download = `${imageName}${suffix}.${format}`;
        link.href = dataURL;
        link.click();
    };
}

function calculateCanvasSize(numberOfImages, imagesPerRow, imageSize, imageMargin) {
    const rows = Math.ceil(numberOfImages / imagesPerRow);
    const canvasWidth = Math.min(
        // Fit imagesPerRow images in a single row; Subtract margin for the last image in the row
        imagesPerRow * (imageSize + imageMargin) - imageMargin,
        // Fit all images in a single row; Subtract margin for the last image in the row
        numberOfImages * (imageSize + imageMargin) - imageMargin
    );
    const canvasHeight = rows * (imageSize + imageMargin) - imageMargin; // Subtract margin for the last row
    return { canvasWidth, canvasHeight };
}

function imagesToRows(array, chunkSize) {
    const result = [];
    let currentIndex = 0;

    while (currentIndex < array.length) {
        const chunk = array.slice(currentIndex, currentIndex + chunkSize);
        result.push(chunk);
        currentIndex += chunkSize;
    }

    return result;
}

function arrangeImageLayout(images, imagesPerRow, imageSize, imageMargin) {
    const imageRows = imagesToRows(Array.from(images), imagesPerRow);
    const imageInfo = []; // { url: string, offsetX: number, offsetY: number, width: number, height: number }
    imageRows.forEach((images, rowIndex) => {
        images.forEach((img, columnIndex) => {
            imageInfo.push({
                url: img.src,
                offsetX: columnIndex * (imageSize + imageMargin),
                offsetY: rowIndex * (imageSize + imageMargin),
                width: imageSize,
                height: imageSize,
            });
        });
    });
    return imageInfo;
}

function handleDownload() {
    console.log("[Download Handler] Start download process");

    // Get the #output-result container element
    const outputResult = document.getElementById("output-result");
    if (!outputResult) {
        console.error("Element #output-result not found.");
        return;
    }

    // Get all images in the #output-result container
    const images = outputResult.querySelectorAll("img");
    if (images.length === 0) {
        console.error("No images found in the output container.");
        return;
    }

    const imagesPerRow = 7;
    const imageSize = 80;
    const imageMargin = 0; // Add some margin between images

    const calligraphyCanvas = document.createElement("canvas");
    const calligraphyCtx = calligraphyCanvas.getContext("2d");

    const { canvasWidth, canvasHeight } = calculateCanvasSize(images.length, imagesPerRow, imageSize, imageMargin);
    calligraphyCanvas.width = canvasWidth;
    calligraphyCanvas.height = canvasHeight;

    const imageLayout = arrangeImageLayout(images, imagesPerRow, imageSize, imageMargin);

    // Draw each image onto the canvas
    let remainingDraws = imageLayout.length;
    imageLayout.forEach((image) => {
        const img = new Image();
        img.crossOrigin = "anonymous"; // Enable CORS for the image
        img.src = image.url;

        img.onload = () => {
            calligraphyCtx.drawImage(img, image.offsetX, image.offsetY, image.width, image.height);

            remainingDraws--;
            if (remainingDraws === 0) {
                console.log("[Download Handler] All images drawn onto the canvas");

                // Trigger the download of the merged image
                initiateImageDownloads(calligraphyCanvas);
            }
        };
    });
}

function initiateImageDownloads(calligraphyCanvas) {
    // Convert the canvas content to a data URL
    const calligraphyImageData = calligraphyCanvas.toDataURL(`image/${format}`);

    const imageName = `ai-calligraphy-output-${getTimestamp()}`;

    // Download the merged image
    // createCanvasDownloadHandler(imageName, "")(calligraphyCanvas);

    // Add white background and download
    addWhiteBackgroundAndDownload(calligraphyImageData, createCanvasDownloadHandler(imageName, `white-bg`));

    // Remove background and download
    removeBackgroundAndDownload(calligraphyImageData, 200, createCanvasDownloadHandler(imageName, `no-bg`));
}

// Function to add a white background to images with a transparent background
function addWhiteBackgroundAndDownload(calligraphyImageData, onCanvasReady) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.crossOrigin = "anonymous"; // Enable CORS for the image
    img.src = calligraphyImageData;

    img.onload = function () {
        canvas.width = img.width;
        canvas.height = img.height;

        // Fill the canvas with white background
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw the image on top of the white background
        ctx.drawImage(img, 0, 0);

        onCanvasReady(canvas);
    };
}

function removeBackgroundAndDownload(calligraphyImageData, threshold, onCanvasReady) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.crossOrigin = "anonymous"; // Enable CORS for the image
    img.src = calligraphyImageData;

    img.onload = function () {
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw the image on the canvas
        ctx.drawImage(img, 0, 0);

        // Get the image data
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;

        // Loop through the pixels and remove the background based on the threshold
        for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];

            // Calculate the average value to determine background
            const average = (r + g + b) / 3;

            if (average > threshold) {
                // Set the pixel to transparent
                pixels[i + 3] = 0;
            }
        }

        // Put the modified image data back to the canvas
        ctx.putImageData(imageData, 0, 0);

        onCanvasReady(canvas);
    };
}

// function downloadImageFromUrl(imageUrl) {
//     fetch(imageUrl)
//         .then((response) => response.blob())
//         .then((blob) => {
//             // Create a temporary URL for the image blob
//             const url = URL.createObjectURL(blob);

//             // Create a temporary <a> element to initiate the download
//             const link = document.createElement("a");
//             link.href = url;
//             link.download = imageUrl.substring(imageUrl.lastIndexOf("/") + 1);
//             link.click();

//             // Clean up the temporary URL
//             URL.revokeObjectURL(url);
//         })
//         .catch((error) => {
//             console.error("Error downloading the image:", error);
//         });
// }
