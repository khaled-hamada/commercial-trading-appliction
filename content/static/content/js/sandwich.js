$(document).ready(function(){
  //  ^ means sta
  divlist = $("div[id^='sand_']");
  divlist.hide();
  $("#search_list_sand").change(function(){

      $(this).find("option:selected").each(function(){
          var optionValue = $(this).attr("value");
          divlist = $("div[id^='sand_']");
          divlist.hide();
          $("#sand_"+optionValue).show();
          // console.log(res);
          // if(optionValue == 1){
          //     $("input").hide();
          //     $("label").hide();
          //
          //     $("#title").show();
          //     // $("option[selected='false']", "#search_list").each(fuction(){
          //     //   $(this).hide();
          //     // });
          //   //  $("otion:unselected").hide();
          // }



      });
  }).change();

  });
