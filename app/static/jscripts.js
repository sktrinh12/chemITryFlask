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

function getComposer() {
  return Kekule.Widget.getWidgetById('kekulecomposer');
}

LINK_WIDTH = 2;
var cname; 

function prepareLinks() {
		linksFromNodes = {};
    links.forEach(function(val, idx) {
      var sid = val.source,
          tid = val.target,
          key = (sid < tid ? sid + "," + tid : tid + "," + sid);
      if (linksFromNodes[key] === undefined) {
        linksFromNodes[key] = [idx];
        val.multiIdx = 1;
      } else {
        val.multiIdx = linksFromNodes[key].push(idx);
      }
      // Calculate target link distance, from the index in the multiple-links array:
      // 1 -> 0, 2 -> 2, 3-> -2, 4 -> 4, 5 -> -4, ...
      val.targetDistance = (val.multiIdx % 2 === 0 ? val.multiIdx * LINK_WIDTH : (-val.multiIdx + 1) * LINK_WIDTH);
    });
}

function calcTranslationExact(targetDistance, point0, point1) {
    var x1_x0 = point1.x - point0.x,
      y1_y0 = point1.y - point0.y,
      x2_x0, y2_y0;
    if (y1_y0 === 0) {
      x2_x0 = 0;
      y2_y0 = targetDistance;
    } else {
      var angle = Math.atan((x1_x0) / (y1_y0));
      x2_x0 = -targetDistance * Math.cos(angle);
      y2_y0 = targetDistance * Math.sin(angle);
    }
    return {
      dx: x2_x0,
      dy: y2_y0
    };
  }

function d3successCallBack(reply) {

        cname = reply.cname;//grabs name from json object in flask view, saves to global var declared above20}
        var checkExist = setInterval( function() { //awaits for ob figure to load first in order to get width of the d3 div
          if ($("#panelContentFigure").length) {
        var figureDiv = document.getElementById("d3-netx-ob"); 
        var svg = d3.select(figureDiv).select("svg");
              height = figureDiv.offsetHeight,
              width = figureDiv.offsetWidth;

				nodes = reply.nodes;
				links = reply.links;

        prepareLinks(); //indexes the second source<->target pairs for double/triple bonds
        //scale that maps to 2 - 4.5 given size as input (domain)
        var radius = d3.scale.sqrt()
            .range([2,4.5]);

         // We create a force-directed dynamic graph layout.
        var force = d3.layout.force()
					.nodes(nodes)
					.links(links)
          .charge(-200)
          .linkDistance(function(d) { return radius(d.source.size) + radius(d.target.size) ; })
          .size([width*0.9, height*0.9]);

          clearInterval(checkExist);
        // In the <div> element, we create a <svg> graphic that will contain our interactive visualization.
        if (svg.empty()) {
          svg = d3.select("#d3-netx-ob").append("svg")
                // .attr("width", width)
                // .attr("height", height)
                .attr("preserveAspectRatio", "xMinYMin meet")
                .attr("viewBox", "0 0 " + width + " " + height)
                .classed("svg-d3-content", true);
        }

        //create the groups under svg to inherit from child elements (so dragging of labels and nodes is tied together)

        var glinks = svg.selectAll('g.link')
            .data(links)
            .enter()
            .append("g")
            .classed('glink',true);
            
        var gnodes = svg.selectAll('g.gnode')
            .data(nodes)
            .enter()
            .append('g')
            .classed('gnode',true)
            .call(force.drag);

              // We load the nodes and links in the force-directed graph.  We create a <line> SVG element for each link in the graph.
              
        var link = glinks
          .append("line")
          .attr("class", "link");

        // We create a <circle> SVG element for each node in the graph, and we specify a few attributes.
        // var node = svg.selectAll(".node")
        var node = gnodes
          .append("circle")
          .attr("class", "node")
          .attr("r", function(d) { return radius(d.size); })
          .style("fill", function(d) {
             // The node color depends on the hex colour code from the networkx object attribute.
             return d.colour_atom;
          })

        var labels = gnodes.append("text")
          .text(function(d) { return d.name; })
          .attr("dy", ".35em")
          .attr("font-size","11px")
          .attr("text-anchor", "middle")
          .attr("font-family", "sans-serif")
          .style('fill', function(d) {
            if(d.colour_atom === "#000000") {
                return "#C2BCB4";
            } else {
                return "#000000";
            }
          });

							//start force simulation
							force.start();
              // We bind the positions of the SVG elements to the positions of the dynamic force-directed graph, at each time step.
              force.on("tick", function() {
                link.attr("x1", function(d){return d.source.x})
                    .attr("y1", function(d){return d.source.y})
                    .attr("x2", function(d){return d.target.x})
                    .attr("y2", function(d){return d.target.y})
                    .attr('transform', function(d) { 
                      var translation = calcTranslationExact(d.targetDistance,d.source, d.target);
                      return `translate (${translation.dx}, ${translation.dy})`;
                    });

                gnodes.attr("transform", function(d) { return 'translate(' + [d.x, d.y] + ')'; });
              });

            } //end of seterinterval fx
            },70); //end of timeout
} //end function

$(document).ready(function() {
  const tablePanel = $("#containTable");
  const kekulecomposer = $("#kekulecomposer");
  var foundResult = $('#found-results');
  //var lblSmrtStr = $('#label_smrtstr');
  tablePanel.hide();
  $("#form-subsrch").hide();
  // $("#d3-netx-ob").hide();
  // $("#panelHeadingInfo").hide();

   if ( $("a#smrtsrch").parent().hasClass('active') && $("button:contains('Draw SMILES')").hasClass('active') ) { 
    var composer = new Kekule.Editor.Composer(document.getElementById('kekulecomposer'));
  composer
    .setEnableCreateNewDoc(false)
    .setEnableLoadNewFile(false)
    .setAllowCreateNewChild(false)
    .setCommonToolButtons([
              'undo', 'redo', 'copy', 'cut', 'paste', 'zoomIn', 'reset', 'zoomOut', 'config', 'objInspector',
              {'name': 'submitSmile',     
                'widget': Kekule.Widget.RadioButton,   // important, set the widget class
                'text': 'Submit', 
                'hint': 'Submit SMILES string', 
                'id': 'SMI-btn' 
              } 
            ]);
  };
/*  function kekulecomposer(elem_to_fill) {
  $(elem_to_fill).html("<div id='kekulecomposer' style='width:700px;'></div>");
  var composer = new Kekule.Editor.Composer(document.getElementById('kekulecomposer'));
  composer
    .setEnableCreateNewDoc(false)
    .setEnableLoadNewFile(false)
    .setAllowCreateNewChild(false)
    .setCommonToolButtons([
              'undo', 'redo', 'copy', 'cut', 'paste', 'zoomIn', 'reset', 'zoomOut', 'config', 'objInspector',
              {'name': 'submitSmile',     
                'widget': Kekule.Widget.RadioButton,   // important, set the widget class
                'text': 'Submit', 
                'hint': 'Submit SMILES string', 
                'id': 'SMI-btn' 
              } 
            ]);
  };

  if ( $("a#smrtsrch").parent().hasClass('active') && $("button:contains('Draw SMILES')").hasClass('active') ) { kekulecomposer("#smi_srch_type"); }else if  ( $("a#smrtsrch").parent().hasClass('active') && $("button:contains('Type SMILES')").hasClass('active') ) {$("#smi_srch_type").html(smrtsrchdashboard);};
*/

  $("#type-smiles").on('click',function() {
    $("#draw-smiles").attr('class', 'list-group-item list-group-item-action');
    $("#type-smiles").attr('class', 'list-group-item list-group-item-action active');
    kekulecomposer.hide();
   $("#form-subsrch").show();

});

  $("#draw-smiles").on('click',function() {
    $("#draw-smiles").attr('class', 'list-group-item list-group-item-action active');
    $("#type-smiles").attr('class', 'list-group-item list-group-item-action');
  kekulecomposer.show();
  $("#form-subsrch").hide();
  });

//kekule composer substructure search
$("#SMI-btn").on('click',function(e) {
  var mols = getComposer().exportObjs(Kekule.Molecule)[0];
  smile_str = Kekule.IO.saveFormatData(mols, 'smi');
  e.preventDefault();
  $.ajax({
    url:'/dplysmrtsrch/',
    data:{smrtstr: smile_str},  
    dataType:'json',
    success:function(reply) {
      // lblSmrtStr.text(`SMARTS string query: ${reply.query}`);
      foundResult.text(`Substructure Search Results - Found ${reply.lengthSrchResult} matches!`);
      foundResult.append(document.createTextNode(` -- SMILES string query: ${reply.query}`));
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

//type smiles in sub-search
$("#form-subsrch").on('submit',function(e) {
	e.preventDefault();
	$.ajax({
		url:'/dplysmrtsrch/',
		data:{smrtstr: $("#smrtsrch_input").val()},  
		dataType:'json',
		success:function(reply) {
			// lblSmrtStr.text(`SMARTS string query: ${reply.query}`);
			foundResult.text(`Substructure Search Results - Found ${reply.lengthSrchResult} matches!`);
      foundResult.append(document.createTextNode(` -- SMILES string query: ${reply.query}`));
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
if ($('#panelContentMain').length != 1)
{
  if (parseInt($('#panelContentMain').html().length)<225) 
  { 
	//console.log($('#panelContentMain').html().length); 
    if($('div#panelHeadingInfo').text().trim().includes('does not exist'))
    {
      $('#panelContentMain').delay(300).show();
    } else { $('#panelContentMain').hide(); }
  }
  else 
    {
  //console.log($('#panelContentMain').html().length);
    $('#panelContentMain').delay(300).show(); 
    }
};



//SHOW LOADING OR INVALID TEXT DURING FORM SUBMISSION
/*$("#form-dplystruc").submit(function( event ) {
  if ( $( "input:first" ).val().toString().length >= 3 ||typeof($("input:first").val()) ==='number' ) {
$( "div#panelContentFigure" ).text( "loading..." ).show();
     return;
	}
	$("div#panelContentFigure" ).text( "Not valid!" ).show().fadeOut( 1000 );
	event.preventDefault();
	});
*/
  //D3 NETWORKX VISUAL

    // First, we specify the size of the canvas
    // containing the visualization (size of the
    // <div> element).
$("#form-dplystruc").on("submit",function(e) 
  {
    e.preventDefault();
    $("#d3-netx-ob").empty();
    $.when(
      $.ajax({//first ajax call
      url:"/updateDplyStrc/",
      data:{csid:$("#csid").val()},
      dataType:'json',
      success: function(reply) {

        var clone = $("div#panelContentFigure").clone(true);
        var figure = $(reply.html_content);
        clone.html(figure);
        $('div#panelContentFigure').replaceWith(clone);

      }
      }),

      $.ajax({//second ajax call -- d3 object
      url:'/exportGraphtoJSON/',
      data:{csid:$("#csid").val()},
      dataType:'json',
      success: d3successCallBack,
      }) //end of 2nd ajax call
      ).done(function() {
        $("#panelHeadingInfo").text(`CSID: ${$("#csid").val()}  |   NAME: ${cname}`);
        $("#d3-netx-ob").show();
        $("#panelContentMain").show();
      }); //end of done
  }); //end submit function

}); //end document ready


    /*
	if ($('#xplrDataTabs').length && !$('#xplrDataTabs ~ .panel.panel-default .panel-body').length) {
	//window.location = '/barplot/';
	console.log($('#xplrDataTabs ~ .panel.panel-default .panel-body').length);
	}


 $("#exploredata").ready(function(){
	$('a[href="/barplot/"]').click();
 	});


document.addEventListener("DOMContentLoaded",function(){
$(window).on('load',function(){
$(document).ready(function(){
	let elementsArray = document.querySelectorAll("#topsvg");
	var tableBody = document.querySelectorAll('tbody');
	console.log(tableBody);
     	let elementsArray = document.querySelectorAll("#topsvg");
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
});

 SWITCH TABS TEST     
function activateTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
}

function switchTab(){
   $(".nav-tabs li:nth-child(2) a").tab('show'); 
};

//bar plot testing (other method)
  $(document).ready(function(){
        $('#updatebarplot').click(function(e){
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
      }); 


	$(window).on('load',function(){
		var data = [];
		$('#topsvg').each(function(){
			data.push($(this).html());
		});
		console.log(data);
	});
  */
