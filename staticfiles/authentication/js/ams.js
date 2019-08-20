var classname_array = document.getElementsByClassName('ams-table__row');
var model = document.getElementsByClassName('bg-modal')[0];
var myFunction = function() {
   model.style.display='flex';
};

for (var i = 0; i < classname_array.length; i++) {
    classname_array[i].addEventListener('click', myFunction, false);
}



document.querySelector('.close').addEventListener('click', function(){
    document.querySelector('.bg-modal').style.display='none';
});





function PopupCenter(url, w, h) {  
              
    width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;  
    height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;  
              
    var left = ((width / 2) - (w / 2));  
    var top = ((height / 2) - (h / 2));  
    var newWindow = window.open(url,'_attview, ' + 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);  
  
    // Puts focus on the newWindow  
    if (window.focus) {  
        newWindow.focus();  
    }  
}  