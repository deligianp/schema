$(document).ready(function()
{
    var status="Init";
    var refreshId;

    $(".cancel-button-container").css('display','inline-block');

    function cleanUp()
    {
    	// var jobid=$("#hidden_jobid_input").val();
     //  	var name=$("#hidden_name_input").val();
    	// $.ajax({
     //        url: "index.php?r=software/clean-up",
     //        type: "GET",
     //        data: { "jobid": jobid, "name": name, 'status': 'Complete'},
     //        dataType: "html",
     //        // success: function (data) 
     //        // {
     //        //   $("#initial-status").hide();
     //        //   $('#pod-logs').html(data); 
              
     //        //   status=$("#status-value").text(); 
     //        //   if (status == "Completed") 
     //        //     {
     //        //       clearInterval(refreshId);
     //        //     }
     //        // },
     //        // retries: 2,
     //        // complete: function() 
     //        // {
     //        // // Schedule the next request when the current one's complete
     //        //   setInterval(sendRequest, 5000); // The interval set to 5 seconds
     //        // },
     //    });
    }
    function cancelClean()
    {
      var jobid=$("#hidden_jobid_input").val();
      var name=$("#hidden_name_input").val();
      $.ajax({
            url: "index.php?r=software/clean-up",
            type: "GET",
            data: { "jobid": jobid, "name": name, "status": "Canceled"},
            dataType: "html",
            success: function (data) 
            {
                clearInterval(refreshId);
                $("#status-value").html("Canceled");
                $(".job-output").hide();
                $(".running-logo").hide();
                $("#command-text-box").removeClass('disabled-box');
                $("#command-text-box").prop('readonly',false);
                $(".cancel-button-container").css('display','none');
                $(".select-mount-button").removeAttr('disabled');
                $(".clear-mount-button").removeAttr('disabled');
                $("#software-start-run-button").removeAttr('disabled');
                $(".select-file-btn").each(function(){
                    $(this).removeAttr('disabled');
                });
                $(".cancel-file-btn").each(function(){
                    $(this).removeAttr('disabled');
                });
                $(".btn_default-values").each(function(){
                    $(this).removeAttr('disabled');
                });

            }
            //   $("#initial-status").hide();
            //   $('#pod-logs').html(data); 
              
            //   status=$("#status-value").text(); 
            //   if (status == "Completed") 
            //     {
            //       clearInterval(refreshId);
            //     }
            // },
            // retries: 2,
            // complete: function() 
            // {
            // // Schedule the next request when the current one's complete
            //   setInterval(sendRequest, 5000); // The interval set to 5 seconds
            // },
        });
    }
    function sendRequest(refId)
    {
      var jobid=$("#hidden_jobid_input").val();
        $.ajax({
                url: "index.php?r=workflow/get-logs",
                type: "GET",
                data: { "jobid":jobid},
                dataType: "html",
                success: function (data) 
                {
                    $("#initial-status").hide();
                    $('#pod-logs').html(data);
              
              
                    status=$("#status-value").text(); 
                    if ( (status == "COMPLETE") || (status == "EXECUTOR_ERROR") )
                    {
                        clearInterval(refId);
                        setTimeout(cleanUp(),2000);
                        totalFields=Number($("#hidden_fieldsNum").val());
      
                        for (i=0; i<=totalFields; i++)
                        {
                            var fieldID="#field-" + i;
                            var field=$(fieldID);
                            field.removeClass('disabled-box');
                            field.prop('readonly',false);
                        }
                        if ((status!='Error') && (status!="ImagePullBackOff"))
                        {
                            // $(".job-output").hide();
                            $(".run-gif-img").hide();

                        }
                        else
                        {
                            $(".run-gif-img").hide();
                        }
                        
                        $("#systemmount").removeClass('disabled-box');
                        $("#systemmount").prop('readonly',false);
                        $("#memory").removeClass('disabled-box');
                        $("#cores").removeClass('disabled-box');
                        $("#systemmount").prop('readonly',false);
                        $("#memory").prop('readonly',false);
                        $("#cores").prop('readonly',false);
                        $(".cancel-button-container").css('display','none');
                        $("#select-active-form-btn").removeClass('disabled-btn');
                        $("#select-non-active-form-btn").removeClass('disabled-btn');
                        $(".select-output-button").removeAttr('disabled');
                        $(".clear-output-button").removeAttr('disabled');
                        $("#software-start-run-button").removeAttr('disabled');
                        $(".select-file-btn").each(function(){
                            $(this).removeAttr('disabled');
                        });
                        $(".clear-file-btn").each(function(){
                            $(this).removeAttr('disabled');
                        });
                        $(".btn-default-values").each(function(){
                            $(this).removeAttr('disabled');
                        });
                        if ($("#has_example").length)
                        {
                            $("#software-run-example-button").removeAttr('disabled');
                        }
                        else
                        {
                            if ($(".add-example-link").length)
                            {
                                $(".add-example-link").show();
                            }
                        }
                    }

                },
                retries: 2,
            // complete: function() 
            // {
            // // Schedule the next request when the current one's complete
            //   setInterval(sendRequest, 5000); // The interval set to 5 seconds
            // },
            });
    }

    $("#software-cancel-button").click(function(){


        clearInterval(refreshId);
        cancelClean();
        totalFields=Number($("#hidden_fieldsNum").val());
        for (i=0; i<=totalFields; i++)
        {
            var fieldID="#field-" + i;
            var field=$(fieldID);
            field.removeClass('disabled-box');
            field.prop('readonly',false);
        }
        $(".job-output").hide()
        $("#isystemmount").removeClass('disabled-box');
        $("#iosystemmount").removeClass('disabled-box');
        $("#osystemmount").removeClass('disabled-box');
        $(".select-mount-button").removeAttr('disabled');
        $(".clear-mount-button").removeAttr('disabled');
        $("#memory").removeClass('disabled-box');
        $("#cores").removeClass('disabled-box');
        $("#systemmount").prop('readonly',false);
        $("#memory").prop('readonly',false);
        $("#cores").prop('readonly',false);
        // $("#command-text-box").removeClass('disabled-box');
        // $("#command-text-box").prop('readonly',false);
        $("#select-active-form-btn").removeClass('disabled-btn');
        $("#select-non-active-form-btn").removeClass('disabled-btn');
        if ($("#has_example").length)
        {
            $("#software-run-example-button").removeAttr('disabled');
        }
        else
        {
            if ($(".add-example-link").length)
            {
                $(".add-example-link").show();
            }
        }

    
    });

    var refreshId = setInterval(function() 
    {
      
      sendRequest(refreshId);
      
    }, 2000);
    
    

})