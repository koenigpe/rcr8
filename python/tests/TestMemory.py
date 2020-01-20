import unittest

import numpy as np

from rl.simple_agent import Memory


class TestMemory(unittest.TestCase):

    def test_add(self):
        m = Memory(2, 5, mem_size=5)

        # Add 5 elements
        [m.add(np.array([x, x]), 1, 1, [x, x], False) for x in range(0, 5)]
        assert (m.cntr == 5)

        # Overwrite first element
        m.add(np.array([6, 6]), 3, 1, [6, 6], False)
        assert (m.mem_state[0][0] == 6.0)

        # Check action
        assert (np.array_equal(m.mem_action[0], np.array((0, 0, 0, 1, 0))))

        # Check counters and shapes
        assert (m.cntr == 6)
        assert (m.mem_action.shape == (5, 5))
        assert (m.mem_reward.shape == (5,))
        assert (m.mem_next_state.shape == (5, 2))
        assert (m.mem_state.shape == (5, 2))
        assert (m.mem_done.shape == (5,))

    def test_add_state_history(self):
        m = Memory(2, 5, mem_size=10, input_history=3)

        # Add elements
        [m.add(np.array([x, x]), 1, 1, [x + 1, x + 1], False) for x in range(0, 10)]

        assert (np.array_equal(m.add_state_history(m.mem_state[3], 3), np.array([0, 0, 1, 1, 2, 2, 3, 3])))
        assert (np.array_equal(m.add_next_state_history(m.mem_next_state[3], 3), np.array([1, 1, 2, 2, 3, 3, 4, 4])))

        with self.assertRaises(ValueError):
            m.add_next_state_history(m.mem_state[2], 2)

    def test_get_current_idx(self):
        m = Memory(2, 5, mem_size=10)

        # Add elements
        [m.add(np.array([x, x]), 1, 1, [x + 1, x + 1], False) for x in range(0, 12)]
        assert(m.get_current_idx() == 1)

    def test_get_blacklist_range(self):
        m = Memory(2, 5, mem_size=10,  input_history=3)

        # Add elements
        [m.add(np.array([x, x]), 1, 1, [x + 1, x + 1], False) for x in range(0, 12)]

        assert((m.get_blacklist_range()) == (2, 4))

    def test_get_sample_idx(self):
        np.random.seed(0)

        m = Memory(2, 5, mem_size=10, input_history=3)
        [m.add(np.array([x, x]), 1, 1, [x + 1, x + 1], False) for x in range(0, 12)]

        assert (np.array_equal(m.get_sample_idx(5), np.array([7, 8, 0, 6, 6])))


if __name__ == '__main__':
    unittest.main()
