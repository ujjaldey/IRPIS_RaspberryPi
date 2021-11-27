class IrpisMainHelper:
    def _is_internet_connected(self):
        return self.common.is_internet_connected(self.config.get_ping_url())

    def _calculate_next_schedule_and_duration(self, conn, curr_schedule):
        return self.common.calculate_next_schedule_and_duration(conn, curr_schedule,
                                                                self.config.get_default_payload_duration_sec())
