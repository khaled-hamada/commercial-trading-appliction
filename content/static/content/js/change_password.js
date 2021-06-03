

$(document).ready(function(){

      $('#change_password').submit(function(){
        var v_1 = $('#password_new_1').val();
        var v_2 = $('#password_new_2').val();

        if(v_1 != v_2){
          // console.log(v_1);
          // console.log(v_2);
          // console.log("تمام التمام");
          console.log("تأكد من تطابق كلمة السر الجديدة فى الخانتي");
          // conform("تأكد من تطابق كلمة السر الجديدة فى الخانتين");
          window.alert("تأكد من تطابق كلمة السر الجديدة فى الخانتين");

          return false;

        }
        else{
          // console.log("تأكد من تطابق كلمة السر الجديدة فى الخانتي");
          // alret("تأكد من تطابق كلمة السر الجديدة فى الخانتين");
          return true;
        }

         // alret("تأكد من تطابق كلمة السر الجديدة فى الخانتين");

      });

});
