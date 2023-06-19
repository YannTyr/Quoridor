from environment import env

env = env(render_mode="human", board_size=(9, 9), walls=4, players=2)
states = env.observation_space("player_0")["observation"].shape
actions = env.action_space("player_0").n


def main():
    env.reset()
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last(observe=True)

        if termination or truncation:
            action = None
            # env.reset() #  ?
        else:
            action = env.action_space(agent).sample(
                observation["action_mask"])
            # action = policy(observation, agent)
        env.step(action)
    env.close()


if __name__ == "__main__":
    main()
