import base64
import datetime
import json
from .util_helper import UtilHelper
from tpt.commons import ActContextEnum, CmpTypeEnum


class TestActivity(UtilHelper):

    def test_create_activity(self):
        tpt = self.get_tpt()

        activity_id = 'vle_id_1_activity_id_1_activity_type_assign'
        course_id = 'course_id_1'
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now()
        activity_type = CmpTypeEnum.AUTO
        context = ActContextEnum.COURSE
        config = json.dumps({"activity_list": [1, 2, 4]})
        data = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. " \
               "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, " \
               "when an unknown printer took a galley of type and scrambled it to make a type " \
               "specimen book. It has survived not only five centuries, but also the leap into " \
               "electronic typesetting, remaining essentially unchanged. It was popularised in " \
               "the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, " \
               "and more recently with desktop publishing software like Aldus PageMaker " \
               "including versions of Lorem Ipsum"
        data_b64 = base64.b64encode(data.encode('utf8'))
        data = self.get_sample_b64_from_content(data_b64, 'plain/text', 'lorem.txt')
        tpt.activity.prepare(activity_id=activity_id, course_id=course_id, start_date=start_date,
                             end_date=end_date, activity_type=activity_type, context=context,
                             config=config, data=data)
        return
        config = tpt.activity.get_config(activity_id=activity_id)

        self.assertEqual(config.activity_id, activity_id)
        self.assertEqual(config.start_date, start_date)
        self.assertEqual(config.end_date, end_date)
    '''
    def test_delete_activity(self):
        # create activity
        self.test_create_activity()
        tpt = self.get_tpt()

        # then delete
        activity_id = 'vle_id_1_activity_id_1_activity_type_assign'
        tpt.activity.delete(activity_id=activity_id)

        config = tpt.activity.get_config(activity_id=activity_id)

        self.assertEqual(config, None)

    def test_archive_activity(self):
        # create activity
        self.test_create_activity()
        tpt = self.get_tpt()

        # then delete
        activity_id = 'vle_id_1_activity_id_1_activity_type_assign'
        tpt.activity.archive_data(activity_id=activity_id)

        config = tpt.activity.get_config(activity_id=activity_id)

        self.assertEqual(config.activity_id, activity_id)
    '''
