import os
import subprocess
import errno

from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.models import Report
from leapp.reporting import report_generic

class RemoveSystemdResumeService(Actor):
    """
    Remove systemd service to launch Leapp.

    After system was rebooted and process resumed, this service is not necessary anymore.
    """

    name = 'remove_systemd_resume_service'
    consumes = ()
    produces = (Report,)
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    def process(self):
        service_name = 'leapp_resume.service'
        if os.path.isfile('/etc/systemd/system/{}'.format(service_name)):
            subprocess.call(['systemctl', 'disable', service_name])
            try:
                os.unlink('/etc/systemd/system/{}'.format(service_name))
                os.unlink('/etc/systemd/system/default.target.wants/{}'.format(service_name))
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        report_generic(
            severity='low',
            title='"{}" service deleted'.format(service_name),
            summary='"{}" was taking care of resuming upgrade process '
                    'after the first reboot'.format(service_name))
