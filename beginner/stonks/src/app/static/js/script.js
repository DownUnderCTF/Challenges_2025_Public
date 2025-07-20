// Get references to the logo and button elements
var logo = document.getElementById('logo');
var button = document.querySelector('button');
const stonkElement = document.getElementById("stonks-vid");
const audioElement2 = document.getElementById("monkenoise");
const audioElement3 = document.getElementById("audio1");
const audioElement4 = document.getElementById("audio2");
const content = document.querySelector(".container-hidden");
var invisibleElements = document.querySelectorAll('.meme');
const imageContainer = document.getElementById('imageContainer');



const body = document.body;

// const backgroundImageUrls = [
//   "/assets/wall1.jpg",
//   "/assets/wall5.gif",
//   "/assets/monkey-music-monkey.gif",
//   "/assets/wall6.gif",
//   "/assets/wall3.jpg",
//   "/assets/wall4.jpg",
//   "/assets/wall7.JPG",
//   "/assets/monke2.gif"
  
// ];




let currentBackgroundIndex = 0;

button.addEventListener('click', function() {
    logo.style.display = 'none';
    button.style.display = 'none';
    stonkElement.play();
    audioElement2.play();
    audioElement3.play();
    audioElement4.play();

    // function changeBackground() {
    //   currentBackgroundIndex = (currentBackgroundIndex + 1) % backgroundImageUrls.length;
    //   const selectedImageUrl = backgroundImageUrls[currentBackgroundIndex];
      
    //   body.style.backgroundColor = "transparent"; // Remove background color
    //   body.style.backgroundImage = `url(${selectedImageUrl})`;
    // }
    
    
    // // Automatically change background image every 3 seconds
    // setInterval(changeBackground, 3000);




    for (var i = 0; i < invisibleElements.length; i++) {
        invisibleElements[i].style.display = 'block';
    }





    const audio = new Audio('/assets/coolsong.mp3'); 

    // document.body.addEventListener('click', () => {
    //   audio.play();
    //  });

    const monday = new Audio('/assets/mondaysound.mp3'); 
    document.body.addEventListener('click', () => {
      monday.play();
    });



    const boom = new Audio('/assets/rasputin-blessing-your-ears-before-blasting-them.mp3'); 
    document.body.addEventListener('click', () => {
      boom.play();
    });



    window.addEventListener('mousemove', function(e) {
        [1, .9, .8, .5, .1].forEach(function(i) {
            var j = (1 - i) * 50;
            var elem = document.createElement('div');
            var size = Math.ceil(Math.random() * 60 * i) + 'px';
            elem.style.position = 'fixed';
            elem.style.top = e.pageY + Math.round(Math.random() * j - j / 2) + 'px';
            elem.style.left = e.pageX + Math.round(Math.random() * j - j / 2) + 'px';
            elem.style.width = size;
            elem.style.height = size;
            elem.style.background = 'hsla(' +
                Math.round(Math.random() * 360) + ', ' +
                '100%, ' +
                '50%, ' +
                i + ')';
            elem.style.borderRadius = size;
            elem.style.pointerEvents = 'none';
            document.body.appendChild(elem);
            window.setTimeout(function() {
                document.body.removeChild(elem);
            }, Math.round(Math.random() * i * 500));
        });
    }, false);

});






//coppied code monke lazy




//coppied code two monke lazy again 