$(document).ready(function(){
  //  ^ means sta
  divlist = $("div[id^='update_product_']");
  divlist.hide();
  $("#search_list_update_product").change(function(){

      $(this).find("option:selected").each(function(){
          var optionValue = $(this).attr("value");
          divlist = $("div[id^='update_product_']");
          divlist.hide();
          $("#update_product_"+optionValue).show();
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
