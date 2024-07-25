const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

const LOADER_PROCESS_STATUS = "Loading";

let cur_session_id = '';
let download_img_name = '';
let image_name = '';
let imageName = '';
let charList = [];

// Get the audio element
// const lanSong = document.getElementById('lanSong');
// const lanSong = new Audio('lantingxu_song.mp3');
// window.onload = function() {
//   playSong();
// }

// Perform actions before the window closes
window.addEventListener('beforeunload', async function (event) {
  event.preventDefault();
  event.returnValue = ''; // Some browsers require a return value

  if (cur_session_id != '') {
    try {
      await clear_res_dir(cur_session_id);
      console.log("Cleaning up files before window closes");
    } catch (error) {
      console.error('Error removing files:', error);
    }
  }
});

async function handleSubmit(event) {
  event.preventDefault();

  download_img_name = '';

  // update_loader("Playing bgm");
  // playSong();

  update_loader("Loading");

  // *************************** Clean up folders from previous gen *****************************
  if (cur_session_id != '') {
    try {
      update_loader("Tidying up");
      await clear_res_dir(cur_session_id);
      console.log("【 handleSubmit() 】generated directories and files removed");
    } catch (error) {
      console.error('Error removing files:', error);
    }
  }


  // *************************** Generate session id *****************************
  var currentTime = new Date();
  let SESSION_ID = String(currentTime.getDate()) + String(currentTime.getHours()) + String(currentTime.getMinutes()) + String(currentTime.getSeconds()) + String(currentTime.getMilliseconds());
  console.log("【 inputCheck() 】Got session id: ", SESSION_ID);
  cur_session_id = SESSION_ID;
  console.log("【 inputCheck() 】Current session id: ", cur_session_id);


  // *************************** Getting and formatting input *****************************
  // Get user input
  charList = [];
  const charInput = document.querySelector('.char-input');
  const charValue = charInput.value;
  // Matching user input into an array
  charList = Array.from(charValue);
  console.log("【 inputCheck() 】obtained character list: ", charList);

  // const strokeInput = document.querySelector('.stroke-input');
  // const strokeValue = strokeInput.value;
  // let strokeList = strokeValue.split(',').map(elem => elem.trim()).filter(elem => elem !== '')
  // console.log("【 inputCheck() 】obtained stroke list: ", strokeList)

  // *************************** Input Checking *****************************
  // let isValidInput = true;
  // 1. Checking if the length of both inputs matches
  // console.log("char length: ", char.length, "stroke length: ", stroke.length)
  // if (charList.length < strokeList.length) {
  //   console.log("【 inputCheck() 】insufficent character input!")
  //   alert("Insufficent character input, please enter enough characters for the stroke inputs");
  //   isValidInput = false;
  // } else if (charList.length > strokeList.length) {
  //   console.log("【 inputCheck() 】insufficent stroke input!")
  //   alert("Insufficent stroke input, please enter enough stroke combinations for the character inputs");
  //   isValidInput = false;
  // }

  // 2. Check if the strokes are all numbers, has 32 digits 
  // const strokeRegex = /^(\d\s?){32}$/
  // strokeList.forEach(checkStroke => {
  //   if ( !(strokeRegex.test(checkStroke)) ) {
  //     console.log("【 inputCheck() 】invalid stroke input")
  //     alert("Invalid stroke input, please enter a 32-digit, number stroke combination seperated by ',' ");
  //     isValidInput = false;
  //   }
  // });

  if (charList.length < 1) {
    console.log("【 inputCheck() 】Empty character input!")
    alert("Empty input, please enter some characters for proper generation");
    resume_default_view();
    return;
  }

  // *************************** Creating content for file saving *****************************
  // Create the content for each file
  const charContent = charList.join(' ');

  // let strokeContent = ''
  // for (i = 0; i < charList.length; i++) {
  //   addStr = charList[i] + " " + strokeList[i];
  //   console.log("addstr: ", addStr);
  //   if (i==0) {
  //     strokeContent = addStr;
  //     console.log("strokeContent: ", strokeContent);
  //   } else {
  //     strokeContent = strokeContent.concat("\n", addStr);
  //     console.log("strokeContent: ", strokeContent);
  //   }
  // }

  console.log("【 handleSubmit() 】Obtained user input")


  // *************************** Saving files and process images *****************************
  try {
    update_loader("Processing inputs");

    // Save char-input.txt
    await saveFile(charContent, 'char-input.txt', SESSION_ID);

    console.log("【 handleSubmit() 】Saved user input to /research/d2/fyp23/lylee0/Font-diff_content/char-input.txt");

    // Save stroke-input.txt
    // await saveFile(strokeContent, 'stroke-input.txt', SESSION_ID);

    // console.log("【 handleSubmit() 】Saved stroke input to /research/d2/fyp23/lylee0/Font-diff_content/stroke-input.txt")

    update_loader("Preparing for generation");

    // Transform txt to img after both inputs are saved
    await font2img(SESSION_ID);

    console.log("【 handleSubmit() 】Transformed txt to png and saved to /research/d2/fyp23/lylee0/content_folder/");

    update_loader("Generating");

    // Generate result img 
    await generate_result(SESSION_ID);

    console.log("【 handleSubmit() 】result generated and saved to /research/d2/fyp23/lylee0/result_web/");

    await display_result(SESSION_ID);

    console.log("【 handleSubmit() 】result displayed; process complete");

  } catch (error) {
    console.error('Error processing files:', error);
    resume_default_view();
  }


}


// Can save directly on browser
// function saveFileLocally(content, fileName) {
//   const element = document.createElement('a');
//   const file = new Blob([content], { type: 'text/plain' });
//   element.href = URL.createObjectURL(file);
//   element.download = fileName;
//   element.click();
// }


// Use GET method instead of POST to avoid body missing error
function saveFile(content, filename, session_id) {
  const encodedContent = encodeURIComponent(content);
  const encodedFilename = encodeURIComponent(filename);
  const encodedSessionId = encodeURIComponent(session_id);
  const front_url = construct_url();
  const req_url = `save-file?content=${encodedContent}&filename=${encodedFilename}&session_id=${encodedSessionId}`;
  const url = front_url.concat(req_url)
  // const url = `http://137.189.88.56:9000/save-file?content=${encodedContent}&filename=${encodedFilename}`;
  // console.log("obtained url: ", url)

  // Clear previous pictures
  const picturesDiv = document.getElementById("pictures");
  picturesDiv.innerHTML = "";

  return new Promise((resolve, reject) => {

    fetch(url)
      .then(function (response) {
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
      .catch(function (error) {
        console.error('An error occurred:', error);
        // Handle the error
        reject();
      });

  })
}


// Transform txt to png by calling server
function font2img(session_id) {
  // const front_url = construct_url();
  // const req_url = `font2img`;
  // const url = front_url.concat(req_url)
  // console.log("obtained url: ", url)

  return new Promise((resolve, reject) => {
    const url = `/font2img?session_id=${session_id}`;

    fetch(url)
      .then(function (response) {
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
      .catch(function (error) {
        console.error('An error occurred:', error);
        // Handle the error
        reject();
      });

  })
}


// Generate samples from server
function generate_result(session_id) {
  // const front_url = construct_url();
  // const req_url = `generate_result`;
  // const url = front_url.concat(req_url)
  // console.log("obtained url: ", url)

  const url = `/generate_result?session_id=${session_id}`;

  console.log('【 generate_result() 】initiating generation.....');

  return new Promise((resolve, reject) => {

    fetch(url)
      .then(function (response) {
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
      .catch(function (error) {
        console.error('An error occurred:', error);
        // Handle the error
        reject();
      });

  })
}


// Display multiple result images
function display_result(session_id) {
  const url = `/get_images?session_id=${session_id}`;

  return new Promise((resolve, reject) => {

    const picturesDiv = document.getElementById('pictures');
    picturesDiv.innerHTML = ""; // Clear previous images

    charList.forEach(char => {
      const img = document.createElement('img');
      let image_name = char + ".png"
      try {
        img.src = `/image/${session_id}/${image_name}`;
      } catch {
        reject();
      }
      img.classList.add('result-image'); // Add a CSS class to the image element
      picturesDiv.appendChild(img);

    });
    document.getElementById("output-result-container").style.display = "block";

    // Hide the loading element
    var loadingElement = document.getElementById("output-loader");
    loadingElement.style.display = "none";

    console.log('【 display_results() 】got result images');

    resolve();

    // fetch(url)
    //   .then(response => response.json())
    //   .then(data => {

    //     const picturesDiv = document.getElementById('pictures');
    //     picturesDiv.innerHTML = ""; // Clear previous images

    //     data.forEach(image => {
    //       const img = document.createElement('img');
    //       img.src = `/image/${session_id}/${image.image_name}`;
    //       img.classList.add('result-image'); // Add a CSS class to the image element
    //       picturesDiv.appendChild(img);
    //       document.getElementById("output-result").style.display = "block";
    //     });

    //     // Hide the loading element
    //     var loadingElement = document.getElementById("output-loader");
    //     loadingElement.style.display = "none";

    //     console.log('【 display_results() 】got result images');

    //     resolve();
    //   })
    //   .catch(error => {
    //     console.error('Error fetching the result images:', error);
    //     reject();
    //   });
  });
}

// Delete generated file and its directory
function clear_res_dir(session_id) {
  const url = `/clear_dir?session_id=${session_id}`;

  return new Promise((resolve, reject) => {
    fetch(url)
      .then(function (response) {
        if (response.ok) {
          console.log('【 clear_res_dir() 】directory: ', session_id, ' cleared sucessfully');
          // Perform any additional actions or show success message
          resolve();
        } else {
          console.error('Failed to clear directory.');
          // Handle the error
          reject();
        }
      })
      .catch(function (error) {
        console.error('An error occurred:', error);
        // Handle the error
        reject();
      });
  });
}


function handleDownload() {
  console.log('【 handleDownload() 】Start download process');

  // Get the #output-result container element
  const outputResult = document.getElementById('output-result');
  if (!outputResult) {
      console.error('Element #output-result not found.');
      return;
  }

  // Get all images in the #output-result container
  const images = outputResult.querySelectorAll('img');
  if (images.length === 0) {
      console.error('No images found in the output container.');
      return;
  }

  const imagesPerRow = 7;
  const imageMargin = 0; // Add some margin between images

  // Calculate the total width and height needed for the merged image
  let totalWidth = 0;
  let totalHeight = 0;
  let currentWidth = 0;
  let currentHeight = 0;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  images.forEach((img, index) => {
      if (index > 0 && index % imagesPerRow === 0) {
          totalHeight += currentHeight + imageMargin;
          currentHeight = 0;
          currentWidth = 0;
      }

      totalWidth = Math.max(totalWidth, currentWidth + img.width);
      currentHeight = Math.max(currentHeight, img.height);
      currentWidth += img.width;
  });

  totalHeight += currentHeight;

  canvas.width = totalWidth;
  canvas.height = totalHeight;

  let offsetX = 0;
  let offsetY = 0;

  // Draw each image onto the canvas
  images.forEach((img, index) => {
      if (index > 0 && index % imagesPerRow === 0) {
          offsetY += currentHeight + imageMargin;
          offsetX = 0;
          currentHeight = 0;
      }

      ctx.drawImage(img, offsetX, offsetY);
      offsetX += img.width + imageMargin;
      currentHeight = Math.max(currentHeight, img.height);
  });

  // Convert the canvas content to a data URL
  const imgData = canvas.toDataURL('image/png');

  // Create a temporary anchor element to trigger the download of the merged image
  const imgAnchor = document.createElement('a');
  imgAnchor.style.display = 'none';
  document.body.appendChild(imgAnchor);

  imgAnchor.href = imgData;
  imgAnchor.download = 'merged_images.png';
  imgAnchor.click();

  // Cleanup
  document.body.removeChild(imgAnchor);
}


function handleDownload1() {

  console.log('【 handleDownload() 】Start download process');

  // Obtain session id for merge and download img
  let session_id = '';
  if (cur_session_id != '') {
    session_id = cur_session_id;
  } else {
    return;
  }


  // If the img is downloaded before, download it again without merging 
  if (download_img_name != '') {
    image_name = download_img_name;
    console.log('【 handleDownload() 】Obtained image_name: ', image_name);
    console.log('【 handleDownload() 】Start downloading merged image');
    downloadImage(`/image/${session_id}/${image_name}`);
    return;
  }

  console.log('【 handleDownload() 】Start merging images');
  const url = `/merge_img?session_id=${session_id}`;

  // Call to merge images on the server
  fetch(url)
    .then(response => {
      if (response.ok) {
        return response.text();
      } else {
        throw new Error('Error fetching the merged images');
      }
    })
    .then(imageName => {
      image_name = imageName;

      // if (download_img_name != '') {
      //   image_name = download_img_name;
      //   console.log('【 handleDownload() 】Obtained image_name: ', image_name);
      //   console.log('【 handleDownload() 】Start downloading merged image');
      //   downloadImage(`/image/${session_id}/${image_name}`);
      //   return;
      // }

      download_img_name = image_name;

      console.log('【 handleDownload() 】Obtained image_name: ', image_name);
      console.log('【 handleDownload() 】Start downloading merged image');
      downloadImage(`/image/${session_id}/${image_name}`);
    })
    .catch(error => {
      console.error('Error fetching the merged images:', error);
    });

}

function downloadImage(imageUrl) {
  fetch(imageUrl)
    .then(response => response.blob())
    .then(blob => {
      // Create a temporary URL for the image blob
      const url = URL.createObjectURL(blob);

      // Create a temporary <a> element to initiate the download
      const link = document.createElement('a');
      link.href = url;
      link.download = imageUrl.substring(imageUrl.lastIndexOf('/') + 1);
      link.click();

      // Clean up the temporary URL
      URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error('Error downloading the image:', error);
    });
}

function construct_url() {

  const host = window.location.hostname;
  const port = 9000;
  const url = `http://${host}:${port}/`;
  console.log('【 construct_url() 】url for site constructed: ', url);

  return url;

}


function update_loader(status) {

  document.getElementById("output-sample").style.display = "none";
  document.getElementById("output-result-container").style.display = "none";
  document.getElementById("output-loader").style.display = "block";

  // Update loader text to current status
  document.getElementById("status").innerText = status;
}

function resume_default_view() {

  document.getElementById("output-sample").style.display = "block";
  document.getElementById("output-result-container").style.display = "none";
  document.getElementById("output-loader").style.display = "none";
}
