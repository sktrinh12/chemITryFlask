person ={name:'Spencer Trinh'};
function myfx() {
   document.write(person.name);
}

/* SWITCH TABS TEST */    
function activateTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
}

function switchTab(){
   $(".nav-tabs li:nth-child(2) a").tab('show'); 
};

/* FORM TEST */
$(function() {
  $('a#procInpt').bind('click', function() {
   $.getJSON('/_bkgProcSmrtSrch', {
     smrtsrch: $('input[name="smrtsrch"]').val(),
   }, function(data) {
     $("#dply").text(data.result);
   });
   return false;
  });
});


/* LOADING SCREEN */
$(document).ready(function() {
  const lockModal = $("#lock-modal");
  const loadingCircle = $("#loading-circle");
  const form = $("#form-subsrch");

  form.on('submit', function(e) {
    e.preventDefault(); //prevent form from submitting

    // lock down the form
    lockModal.css("display", "block");
    loadingCircle.css("display", "block");

    form.children("input").each(function() {
            $(this).attr("readonly", true);
            });
    
    // re-enable the form
     $(document).ready(function() { 
       $('#form-subsrch').submit(function(){
         lockModal.css("display", "none");
         loadingCircle.css("display", "none");
      
       form.children("input").each(function() {
         $(this).attr("readonly", false);
        }); 
     });
  });
});
});
//function loading(){
  //          $("#loading-circle").show();
    //        $("#lock-modal").hide();       
      //  }

      //  function preloader(form){
        //    document.getElementById("loading-circle").style.display = "none";
          //  document.getElementById("lock-modal").style.display = "block";
       // }//preloader
       // window.onload = preloader;
