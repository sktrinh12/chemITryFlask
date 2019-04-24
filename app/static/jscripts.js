$.ajaxSetup({
	beforeSend: function(){
	   $("#lock-modal").css('display','block');
	   $("#loading-circle").css('display','block');
		 },
	complete: function(){
	   $("#lock-modal").css("display","none");
	   $("#loading-circle").css("display","none");   
		 }
	 });

$(document).ready(function() {

  const form = $("#form-subsrch");
  const tablePanel = $("#containTable");
  var foundResult = $('#found-results');
  var lblSmrtStr = $('#label_smrtstr');
  tablePanel.hide();
  form.on('submit',function(e) 
	{	
	e.preventDefault();
	$.ajax({
		url:'/dplysmrtsrch/',
		data:{smrtstr: $("#smrtsrch_input").val()},  
		dataType:'json',
		success:function(reply) {
			lblSmrtStr.text(`SMARTS string query: ${reply.query}`);
			foundResult.text(`Substructure Search Results - Found ${reply.lengthSrchResult} matches!`);
			tablePanel.show();
			$('#table-results').html(reply.htmlTable).fadeIn(500);
			$('#found-results').fadeIn(100);
			},
		error: function(err)
			{
			console.log(err);
			alert('Error occured!'+'('+err+')');
			}
      	} );
     	return false; //returns nothing if doesn't run thru code
  } ); 
//BARPLOT JAVASCRIPT
 $('#form-barplot').submit(function (event) {
		event.preventDefault();
		if ($('#form-barplot')[0].checkValidity() === false) 
			{
			event.stopPropagation();
			 
		 } else {
			$.getJSON('/updateBar/', 
				{
			    	binNum: $("#barplotBinNum").val() 
			        },
				function(data) 
				{
				  $('#barplot-content').html(data.html_plot);
				});
		};
		return false;
 	}); 

//DISPLAY TANIMOTO HEATMAP OR NETWORKX GRAPH OR CHEMICAL STRUCTURE UPON CLICK

	function AJAXcallPaneLink(IDelem,url) 
		{
		IDelem.click(function(e) {
		e.preventDefault();
		$.ajax({
			url:url,
			data:{'csid':parseInt($('div#panelHeadingInfo').text().split('ChemSpider ID:')[1].trim())},
			success: function(data) {
				// console.log($(data.csid));
				$('a.active').not('#dplystruc').attr('class','list-group-item'); //select the a tag that is active but not incl the main nav tab and change its class to normal
				IDelem.attr('class', 'list-group-item active');
				var clone = $("div#panelContentFigure").clone(true);
				var figure = $(data.html_content);
				clone.html(figure);
				$('div#panelContentFigure').replaceWith(clone).slideUp(250);
				}
			});
		});
	}
	if($('#panelHeadingInfo').text().length >34){ //there is a csid & cname in the panel header
		alink_tani = $('a#tanimoto');
		alink_molec = $('a#dplymolec');
		alink_tani.attr('href','#'); //make clickable
		alink_netx = $('a#netx');
		alink_netx.attr('href','#');
		AJAXcallPaneLink(alink_tani,'/updateTani/');
		AJAXcallPaneLink(alink_molec,'/updateDplyStrc/'); //if click on any of these a tag links, will make ajax call to update figure within the div
		AJAXcallPaneLink(alink_netx,'/updateNetx/');
}

//HIDE THE DIV IF THERE IS NO CSID ENTERED	
if ($('#panelContentMain').length){
  if (parseInt($('#panelContentMain').html().length)<200   ) { 
	console.log($('#panelContentMain').html().length); 
	if($('div#panelHeadingInfo').text().trim().includes('does not exist')){
		$('#panelContentMain').delay(300).show();
	} else{

	$('#panelContentMain').hide();
	}
}
else {
	console.log($('#panelContentMain').html().length);
	$('#panelContentMain').delay(300).show(); 
}
};
//SHOW LOADING OR INVALID TEXT DURING FORM SUBMISSION
$("#form-dplystruc").submit(function( event ) {
	if ( $( "input:first" ).val().toString().length >= 3 ||typeof($("input:first").val()) ==='number' ) {
	$( "div#panelContentFigure" ).text( "loading..." ).show();
       return;
	}
	$("div#panelContentFigure" ).text( "Not valid!" ).show().fadeOut( 1000 );
	event.preventDefault();
	});



}); 


	//if ($('#xplrDataTabs').length && !$('#xplrDataTabs ~ .panel.panel-default .panel-body').length) {
	////window.location = '/barplot/';
	//console.log($('#xplrDataTabs ~ .panel.panel-default .panel-body').length);
	//}


// $("#exploredata").ready(function(){
// 	$('a[href="/barplot/"]').click();
// 	});


//FOR SUBSTRUCTURE SEARCH RESULTS (ZOOM IN ON STRUCTURES)
//document.addEventListener("DOMContentLoaded",function(){
//$(window).on('load',function(){
//$(document).ready(function(){
	//let elementsArray = document.querySelectorAll("#topsvg");
	//var tableBody = document.querySelectorAll('tbody');
	//console.log(tableBody);
     /*	let elementsArray = document.querySelectorAll("#topsvg");
	console.log(elementsArray);
	elementsArray.forEach(function(elem) {
	    elem.addEventListener("click", function(){
		    var title = elem.getElementsByTagName('title')[0].innerHTML.replace(' - Open Babel Depiction','');
		    var clone = elem.cloneNode(true);
		    clone.setAttribute('width','550px');
		    clone.setAttribute('height','550px');
		    //console.log('width: ' + clone.getAttribute('width'));
		    //console.log('height: ' + clone.getAttribute('height'));
		$('#svgmodal').css("display","block");
		$('#svgimg').html(clone); 
		$('#caption').text(title);
	  return false;
	 });
		$('#xclose').click(function () {
		$('#svgmodal').css("display","none");
	    });
    });
//});
*/

/* SWITCH TABS TEST     
function activateTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
}

function switchTab(){
   $(".nav-tabs li:nth-child(2) a").tab('show'); 
};
*/

/*bar plot testing (other method)
  $(document).ready(function(){
        $('#updatebarplot').click(function(e){
          // prevent page being reset, we are going to update only
          // one part of the page.
          e.preventDefault()
          var inputdata = $("#barplotBinNum").val();
          $.ajax({
            url:"./update_barplot",
            type:'POST',
            data:{'binNum':inputdata},
            success : function(data){
              // server returns rendered "update_content.html"
              // which is just pure html, use this to replace the existing
              // html within the "plot content" div
              $('#barplot-content').html(data);
             
            }
          })
        });
      }); */


	// $(window).on('load',function(){
	// 	var data = [];
	// 	$('#topsvg').each(function(){
	// 		data.push($(this).html());
	// 	});
	// 	console.log(data);
	// });
