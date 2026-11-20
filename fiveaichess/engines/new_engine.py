from fiveaichess.agents.new_agent import NewAgent
from fiveaichess.utilities.new_utility import NewUtility
from fiveaichess.engines.uci_engine import UCIEngine

if __name__ == "__main__":
    # create your utility
    utility = NewUtility()
    # create your agent
    agent = NewAgent(utility, 5.0)
    # create the engine
    engine = UCIEngine(agent)
    
    # run the engine (will loop until the game is done or exited)
    engine.run()
