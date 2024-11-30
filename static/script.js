const element = document.querySelector(".flash-message");
const button = document.querySelector(".close-button");

if (element){
    button.onclick = function(){
        element.remove();
    };
    setTimeout(() => {
        element.remove();        
    }, 20000);
};
