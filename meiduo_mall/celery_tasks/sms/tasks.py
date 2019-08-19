from celery_tasks.main import app


@app.task
def ccp_send_sms_code(mobile,sms_code):

    '''发送短信异步任务'''

    from libs.yuntongxun.sms import CCP
    send_result = CCP().send_template_sms(mobile,[sms_code,5],1)
    print(send_result)
    return send_result


