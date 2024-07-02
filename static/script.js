const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

const LOADER_PROCESS_STATUS = "Loading";

async function handleSubmit(event) {
  event.preventDefault();

  update_loader("Loading");

  // Get user input
  const charInput = document.querySelector('.char-input');
  const strokeInput = document.querySelector('.stroke-input');
  const charValue = charInput.value;
  const strokeValue = strokeInput.value;

  // Create the content for each file
  const charContent = charValue;
  const strokeContent = charValue + " " + strokeValue;

  console.log("【 handleSubmit() 】Obtained user input and stroke input")


  try {
    update_loader("Processing inputs");

    // Save char-input.txt
    await saveFile(charContent, '/research/d2/fyp23/lylee0/Font-diff_content/char-input.txt');

    console.log("【 handleSubmit() 】Saved user input to /research/d2/fyp23/lylee0/Font-diff_content/char-input.txt")

    // Save stroke-input.txt
    await saveFile(strokeContent, '/research/d2/fyp23/lylee0/Font-diff_content/stroke-input.txt');

    console.log("【 handleSubmit() 】Saved stroke input to /research/d2/fyp23/lylee0/Font-diff_content/stroke-input.txt")

    update_loader("Preparing for generation");

    // Transform txt to img after both inputs are saved
    await font2img() 

    console.log("【 handleSubmit() 】Transformed txt to png and saved to /research/d2/fyp23/lylee0/content_folder/")

    update_loader("Generating");

    // Generate result img 
    await generate_result()

    console.log("【 handleSubmit() 】result generated and saved to /research/d2/fyp23/lylee0/result_web/")

    display_result()

    console.log("【 handleSubmit() 】result displayed; process complete")

  } catch (error) {
    console.error('Error processing files:', error);
  }
  
  // os.system('chmod -R 777 /research/d2/fyp23/lylee0/Font-diff_content/');
  
  // Display result (to be updated)
  // const outputContainer = document.querySelector('.output-container');
  // const outputImg = document.querySelector('#output-img');
  // outputImg.setAttribute('src', ' ');

}


// Can save directly on browser
// function saveFileLocally(content, fileName) {
//   const element = document.createElement('a');
//   const file = new Blob([content], { type: 'text/plain' });
//   element.href = URL.createObjectURL(file);
//   element.download = fileName;
//   element.click();
// }


// Use POST method but can only test through postman
// function saveFileUsingPOST(content, filename) {
// const formData = new FormData();
// const blob = new Blob([content], { type: 'text/plain' });
// formData.append('file', blob, filename);

// fetch('http://137.189.88.153:9000/save-file', {
// method: 'POST',
// body: formData
// })
// .then(function(response) {
// if (response.ok) {
// console.log('File saved successfully.');
// // Perform any additional actions or show success message
// } else {
// console.error('Failed to save file.');
// // Handle the error
// }
// })
// .catch(function(error) {
// console.error('An error occurred:', error);
// // Handle the error
// });
// }


// Use GET method instead of POST to avoid body missing error
function saveFile(content, filename) {
  const encodedContent = encodeURIComponent(content);
  const encodedFilename = encodeURIComponent(filename);
  const front_url = construct_url();
  const req_url = `save-file?content=${encodedContent}&filename=${encodedFilename}`;
  const url = front_url.concat(req_url)
  // const url = `http://137.189.88.56:9000/save-file?content=${encodedContent}&filename=${encodedFilename}`;
  // console.log("obtained url: ", url)


  return new Promise((resolve, reject) => {

    fetch(url)
    .then(function(response) {
      if (response.ok) {
        console.log('【 saveFile() 】File saved successfully.');

        // Perform any additional actions or show success message
        resolve();
      } else {
        console.error('Failed to save file.');
        // Handle the error
        reject();
      }
    })
    .catch(function(error) {
      console.error('An error occurred:', error);
      // Handle the error
      reject();
    });

  })
}


// Transform txt to png by calling server
function font2img() {
  // const front_url = construct_url();
  // const req_url = `font2img`;
  // const url = front_url.concat(req_url)
  // console.log("obtained url: ", url)

  return new Promise((resolve, reject) => {

    fetch('/font2img')
    .then(function(response) {
      if (response.ok) {
        console.log('【 font2img() 】txt transformed to png sucessfully');
        // Perform any additional actions or show success message
        resolve();
      } else {
        console.error('Failed to transform txt.');
        // Handle the error
        reject();
      }
    })
    .catch(function(error) {
      console.error('An error occurred:', error);
      // Handle the error
      reject();
    });

  })
}


// Generate samples from server
function generate_result() {
  // const front_url = construct_url();
  // const req_url = `generate_result`;
  // const url = front_url.concat(req_url)
  // console.log("obtained url: ", url)
  console.log('【 generate_result() 】initiating generation.....');

  return new Promise((resolve, reject) => {

    fetch('/generate_result')
    .then(function(response) {
      if (response.ok) {
        console.log('【 generate_result() 】result generated!');
        // Perform any additional actions or show success message
        resolve();
      } else {
        console.error('Failed to generate result.');
        // Handle the error
        reject();
      }
    })
    .catch(function(error) {
      console.error('An error occurred:', error);
      // Handle the error
      reject();
    });

  })
}


function display_result() {
  
  fetch('/get_image')
    .then(response => response.json())
    .then(data => {
        const result_img = document.getElementById('output-img');
        result_img.src = `/image/${data.image_name}`;
        console.log('【 display_result() 】got result img');

        document.getElementById("output-loader").style.display = "none";
        document.getElementById("output-result").style.display = "block";
    })
    .catch(error => console.error('Error fetching the result image:', error));

}


function construct_url() {

  const host = window.location.hostname;
  const port = 9000; 
  const url = `http://${host}:${port}/`;
  console.log('【 construct_url() 】url for site constructed: ', url);

  return url;

}


function update_loader(status) {

  document.getElementById("output-result").style.display = "none";
  document.getElementById("output-loader").style.display = "block";

  // Update loader text to current status
  document.getElementById("status").innerText = status;
}