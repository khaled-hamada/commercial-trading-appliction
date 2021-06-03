$(document).ready(function(){
  //  ^ means sta
  divlist = $("div[id^='sell_product']");
  divlist.hide();

  $("#search_list").change(function(){

      $(this).find("option:selected").each(function(){
          var optionValue = $(this).attr("value");
          divlist = $("div[id^='sell_product']");
          divlist.hide();
          $("#sell_product_"+optionValue).show();
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

          //  hide sub_product div at start
          // $("#sub_product_div").hide();
          // $("#sub_product_div :input").attr('required', false);
          $("#toggle").click(function(){

               if($("#toggle").text() == "إخفاء"){
                 $("#toggle").text("إظهار");
                 $("#sub_product_div").hide();
                 $("#sub_product_div :input").attr('required', false);
                 // $("#sub_product_div :input").hide();
               }
               else{
                 $("#toggle").text("إخفاء");
                 $("#sub_product_div").show();
                $("#sub_product_div :input").attr('required', true);
                  // $("#sub_product_div :input").show();
               }

               // $('.required').prop('required', function(){
               //   return  $(this).is(':visible');
               // });

            });



  });
