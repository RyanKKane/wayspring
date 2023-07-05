# wayspring-eval

## Files included

+ NuWellness-AfterHours.png = This is a diagram of the code that would be deployed
+ Setup-Basics.yaml = This is the cloud formation template to create the code commit repo, IAM users to run different parts of the process, S3 bucket for the pipeline, etc.
+ Setup-Pipeline.yaml = This creates the pipeline which when triggered will call various component files from the AppInfrastructure folder (broken out by service for ease of updates when services change or get replaced, etc)
+ sms.json = Corrected sample json message
+ lambda.py = This is the lambda code that would run the process of checking for SMS messages, validating it should send a new one, sending as needed and logged once sent.

## Assumptions

There were a few assumptions made to get this all working as follows:

1. Times listed in the use case are different time / timezone from the requirements. Defined windows will be 8:00am - 5:00pm CT (Monday-Friday) for business hours. 5:00pm - 8:00am CT (Plus all weekend) for the After-hours window.
2. The sample JSON provided is not a valid JSON message. This has been corrected for the missing " marks and , marks to make the JSON valid. (It is assumed this was just a typo and the response from the 3rd party API is correct)
3. No details on if the third party API is doing a push to me and I should be listening for that or make a pull (assuming it's a pull) but there are no details on if there are multiple messages on a pull or just have to make continuous pulls until no response? The assumption made is a single request (on a 1min timer) will return a singular JSON message about an SMS message sent.
4. It was mentioned that all traffic/data should be secured but did not indicate that we needed special KMS keys so default AWS keys are used. This will help keep costs down as well.

## Questions / Statement

1. The biggest issue is that due to recent rules that AWS must adhere to the only way to send SMS messages from AWS is to setup an origination number. Depending on the type this can be take anyways from 1 business week to 12 weeks. So while the code should in theory send a SMS message and work there is no way to test this.
2. I have never deployed python code that I have written. All previous codepipeline work was deploying code written and packaged by others. Because the code won't work due to no valid API to pull from and can't send SMS texts this is mostly just theory.
3. There was very little error checking put into the code or pipelines to alert on failures.
4. Once the Setup-Basics.yaml was run via Cloud Formation there is a bucket called s3-afterhours-lambda that needs to have the ZIP file (lambda_deployment_package.zip) with the lambda code placed there for deployment.
