const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

function handleSubmit(event) {
  event.preventDefault();

  // Get user input
  const charInput = document.querySelector('.char-input');
  const userInput = charInput.value;

  // Display result
  const outputContainer = document.querySelector('.output-container');
  const outputImg = document.querySelector('#output-img');
  outputImg.setAttribute('src', ' ');

  const stampImg = document.querySelector('#stamp');
  stampImg.setAttribute('src', './front-end/wanxizhi_stamp.png');
}
