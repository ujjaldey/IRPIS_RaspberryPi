class IrpisMainHelper:
    def _is_internet_connected(self):
        return self.common.is_internet_connected()

    def _calculate_next_schedule_and_duration(self, conn, curr_schedule):
        return self.common.calculate_next_schedule_and_duration(conn, curr_schedule)
