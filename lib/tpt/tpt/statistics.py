"""
TPTStatisticsHelper module
"""
import time
from tpt.commons import StatisticTypeEnum
from tpt.model import TPTStatistics


class TPTStatisticsHelper:
    """
    TPTStatisticsHelper class
    """
    def __init__(self, data, settings):
        self.data = data
        self.enabled = bool(settings.get('Statistics', 'enabled'))
        self.statistics = {}

    def start_elapsed_time_statistic(self, stat_id, name):
        """
        Get start elapsed time statistic
        :param stat_id:
        :param name:
        :return:
        """
        if self.enabled:

            self.statistics[self.get_id(stat_id, name)] = time.time()

    def end_elapsed_time_statistic(self, stat_id, name):
        """
        Get end elapsed time statistic
        :param stat_id:
        :param name:
        :return:
        """
        if self.enabled:
            # time in milliseconds
            elapsed_time = (time.time() - self.statistics.pop(self.get_id(stat_id, name))) * 1000
            statistic = TPTStatistics(item_id=str(stat_id), type=StatisticTypeEnum.ELAPSED_TIME,
                                      name=name, value=elapsed_time)
            self.data.add_statistic(statistic)

    @staticmethod
    def get_id(stat_id, statistic):
        """
        Get statistic id
        :param stat_id:
        :param statistic:
        :return:
        """
        return statistic + '_' + str(stat_id)

    def get_health_data(self):
        """
        Get health data
        :return:
        """
        return self.data.get_health_data()
