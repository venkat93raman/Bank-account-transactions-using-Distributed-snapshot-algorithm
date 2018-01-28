# Bank account transactions using Distributed snapshot algorithm
The goal of the project was to implement distributed system to simulate bank transactions. In this project, each client present will transfer random money at a regular interval of time. A snapshot is taken which represents the money present at both sending and receiving accounts along with the money on the fly (channel state) which is the money deducted from the account of the client but not posted. The snapshot is taken when required and can be then used to retrieve the state during failures.
