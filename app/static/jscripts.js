/* SWITCH TABS TEST */    
function activateTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
}

function switchTab(){
   $(".nav-tabs li:nth-child(2) a").tab('show'); 
};

/* FORM TEST 
$(function() {
  $('#form-barplot').bind('click', function() {
   $.getJSON('/_bkgProcSmrtSrch', {
     binNum: $('input[name="barplotBinNum"]').val(),
   }, function(data) {
     $("#dply").text(data.result);
   });
   return false;
  });
});*/ 

$(document).ready(function(){
        $('#updatebarplot').click(function(e){
          // prevent page being reset, we are going to update only
          // one part of the page.
          e.preventDefault()
          var inputdata = $("#barplotBinNum").val();
          $.ajax({
            url:"{{ url_for('update_barplot') }}",
            type:'POST',
            data:JSON.stringify({'binNum':inputdata}),
            success : function(data){
              // server returns rendered "update_content.html"
              // which is just pure html, use this to replace the existing
              // html within the "plot content" div
              $('#barplot-content').html(data);
             
            }
          })
        });
      });

/* LOADING SCREEN` 
$(document).ready(function() { 
  const lockModal = $("#lock-modal");
  const loadingCircle = $("#loading-circle");
  const form = $("#form-subsrch");
  var stringPattern = $('textarea[name=smrtsrch]').val();  
  form.on(
	  'submit',
	  function(e){
	  	lockModal.css('display','block');
	  	loadingCircle.css('display','block');
  
   //e.preventDefault(); //prevent form from submitting

   //lock down the form  
   lockModal.css("display","block");
   loadingCircle.css("display","block");
     $.ajax(
	     {
      url:"{{ url_for('smrtsrch') }}",
      type:'POST', 
      data: {'smrtstr': stringPattern},  
      success:function(response) {
      console.log(response);
      lockModal.css("display","none");
      loadingCircle.css("display","none");        
      $('#table-results').show();
      $('#found-results').fadeIn(100);
      },
      error: function(err){
         alert('Error occured!'+'('+err+')');
      }
      });
     return false; //important to stay on page without reload?
  });
});
*/

  
 




    




      
  



