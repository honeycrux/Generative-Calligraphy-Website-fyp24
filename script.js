const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

function handleSubmit(event) {
  event.preventDefault();

  // Get user input
  const charInput = document.querySelector('.char-input');
  const strokeInput = document.querySelector('.stroke-input');
  const charValue = charInput.value;
  const strokeValue = strokeInput.value;

  // Create the content for each file
  const charContent = charValue;
  const strokeContent = charValue + " " + strokeValue;

  // Save char-input.txt
  saveFile(charContent, '/research/d2/fyp23/lylee0/Font-diff_content/char-input.txt');

  // Save stroke-input.txt
  saveFile(strokeContent, '/research/d2/fyp23/lylee0/Font-diff_content/stroke-input.txt');

  // os.system('chmod -R 777 /research/d2/fyp23/lylee0/Font-diff_content/');

  // Display result (to be updated)
  const outputContainer = document.querySelector('.output-container');
  const outputImg = document.querySelector('#output-img');
  outputImg.setAttribute('src', ' ');

}


// Can save directly on browser
function saveFileLocally(content, fileName) {
  const element = document.createElement('a');
  const file = new Blob([content], { type: 'text/plain' });
  element.href = URL.createObjectURL(file);
  element.download = fileName;
  element.click();
}


// Use POST method but can only test through postman
function saveFileUsingPOST(content, filename) {
const formData = new FormData();
const blob = new Blob([content], { type: 'text/plain' });
formData.append('file', blob, filename);

fetch('http://137.189.88.154:9000/save-file', {
method: 'POST',
body: formData
})
.then(function(response) {
if (response.ok) {
console.log('File saved successfully.');
// Perform any additional actions or show success message
} else {
console.error('Failed to save file.');
// Handle the error
}
})
.catch(function(error) {
console.error('An error occurred:', error);
// Handle the error
});
}


// Use GET method instead of POST to avoid body missing error
function saveFile(content, filename) {
  const encodedContent = encodeURIComponent(content);
  const encodedFilename = encodeURIComponent(filename);
  const url = `http://137.189.88.153:9000/save-file?content=${encodedContent}&filename=${encodedFilename}`;

  fetch(url)
    .then(function(response) {
      if (response.ok) {
        console.log('File saved successfully.');
        // Perform any additional actions or show success message
      } else {
        console.error('Failed to save file.');
        // Handle the error
      }
    })
    .catch(function(error) {
      console.error('An error occurred:', error);
      // Handle the error
    });
}

function createTextFile() {

}
