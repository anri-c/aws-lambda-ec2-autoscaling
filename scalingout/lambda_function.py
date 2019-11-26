import boto3
import json, logging, time,

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cp = boto3.client('codepipeline')
asg = boto3.client('autoscaling')


def put_job_success(job_id):
    cp.put_job_success_result(jobId=job_id)

def put_job_failure(job_id):
    cp.put_job_failure

def get_inservice_instances(autoscaling_group):
    res = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            autoscaling_group,
        ],
    )

    desired_capacity = res['AutoScalingGroups'][0]['DesiredCapacity']
    max_size = res['AutoScalingGroups'][0]['MaxSize']
    instances = res['AutoScalingGroups'][0]['Instances']

    inservice_instance_count = 0
    for instance in instances:
        state = instance.get('LifecycleState')
        if state == 'InService':
            inservice_instance_count += 1

    result = {
        'name': autoscaling_group,
        'max_size': int(max_size),
        'desired_capacity': int(desired_capacity),
        'inservice_instance_count': int(inservice_instance_count)
    }
        
    return result

def scaling_out_action(obj):
    loggre.info('Starting scale-out')

    autoscaling_group_name = obj['name']
    current_max_size = obj['max_size']
    current_desired_capacity = obj['desired_capacity']

    demand_max_size = current_max_size * 2
    demand_desired_capacity = current_desired_capacity * 2
    
    req = asg.update_autoscaling_group(
        AutoScalingGroupName=autoscaling_group_name,
        MaxSize=demand_max_size,
        DesiredCapacity=demand_desired_capacity
    )

    res = {
        'demand_max_size': int(demand_max_size),
        'demand_desired_capacity': int(demand_desired_capacity)
    }

    return res


def lambda_handler(event, context):
    retry_count = 25

    try:
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        user_parameters = job_data['actionConfiguration']['configuration']

        pipelinename = user_parameters['PipelineName']

        asg_info = get_inservice_instances()
        scaling_out_req = scaling_out_action(asg_info)
        
        for i in range(1, 1 + retry_count)
            new_asg_info = get_inservice_instances()
            
            if new_asg_info['inservice_instance_count'] = scaling_out_req['demand_desired_capacity']:
                put_job_success(job_id)
                break
            else:
                time.sleep(30)

        else:
            put_job_failure(job_id, msg)
    except Exception as err:
        logger.error(err)
        put_job_failure(job_id)

    return None
