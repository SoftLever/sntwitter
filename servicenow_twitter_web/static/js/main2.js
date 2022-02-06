$(function(){
	$("#wizard").steps({
        headerTag: "h4",
        bodyTag: "section",
        transitionEffect: "fade",
        enableAllSteps: true,
        transitionEffectSpeed: 500,
        onStepChanging: function (event, currentIndex, newIndex) { 
            if ( currentIndex === 0 ) {
                $('.steps ul').addClass('step-2');
                // Submit all primary details
                // var csrftoken = csrftoken; // $('input[name="csrfmiddlewaretoken"]').val();
                var first_name = $('#first_name').val();
                var last_name = $('#last_name').val();
                var company_name = $('#company_name').val();
                var email = $('#email').val();
                var password = $('#password').val();

                $.ajax({
                    // headers: { "X-CSRFToken": csrftoken },
                    type: "GET",
                    url: '',                   
                    data: {
                      'first_name': first_name,
                      'last_name': last_name,
                      'email': email,
                      'company_name': company_name,
                      'password': password    
                    },
                    success: function (data) {  
                      console.log('Created User');
                    }
                });

                $('.primary-details').attr("disabled", "true");
            } else {
                $('.steps ul').removeClass('step-2');
            }
            if ( currentIndex === 1 ) {
                $('.steps ul').addClass('step-3');
                // var csrf_token = csrftoken; // $('input[name="csrfmiddlewaretoken"]').val();
                var sn_url = $('#sn_url').val();
                var sn_admin = $('#sn_admin').val();
                var sn_admin_pwd = $('#sn_admin_pwd').val();
                var sn_customer = $('#sn_customer').val();
                var sn_customer_pwd = $('#sn_customer_pwd').val();
                var sn_customer_acc = $('#sn_customer_acc').val();

                $.ajax({
                    // headers: { "X-CSRFToken": csrftoken },
                    type: "GET",
                    url: '/servicenow-reg/',                   
                    data: {
                      'sn_url': sn_url,
                      'sn_admin': sn_admin,
                      'sn_admin_pwd': sn_admin_pwd,
                      'sn_customer': sn_customer,
                      'sn_customer_pwd': sn_customer_pwd,
                      'sn_customer_acc': sn_customer_acc     
                    },
                    success: function (data) {  
                      console.log('Added ServiceNow details');
                    }
                });

                $('.sn-details').attr("disabled", "true");

            } else {
                $('.steps ul').removeClass('step-3');
            }

            if ( currentIndex === 2 ) {
                $('.steps ul').addClass('step-4');
                $('.actions ul').addClass('step-last');
                // re-direct to twitter auth
                window.location.href="/addtwitteraccount/";
            } else {
                $('.steps ul').removeClass('step-4');
                $('.actions ul').removeClass('step-last');
            }
            return true; 
        },
        labels: {
            finish: "Go to Twitter",
            next: "Next",
            previous: "Previous"
        }
    });
    // Custom Steps Jquery Steps
    $('.wizard > .steps li a').click(function(){
    	$(this).parent().addClass('checked');
		$(this).parent().prevAll().addClass('checked');
		$(this).parent().nextAll().removeClass('checked');
    });
    // Custom Button Jquery Steps
    $('.forward').click(function(){
    	$("#wizard").steps('next');
    })
    $('.backward').click(function(){
        $("#wizard").steps('previous');
    })
    // Checkbox
    $('.checkbox-circle label').click(function(){
        $('.checkbox-circle label').removeClass('active');
        $(this).addClass('active');
    })
})
