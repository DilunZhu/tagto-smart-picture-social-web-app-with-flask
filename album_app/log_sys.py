def log_request(req: 'flask_request', res: str) -> None:
    """日志系统"""
    with open('photo_analyse.log','a') as log:
        print(req.form, req.remote_addr, req.user_agent, res, file=log, sep='|')
