import { ConversationItem } from '../types/conversation';

export const MOCK_CONVERSATIONS: ConversationItem[] = [
  {
    id: 'conv-01',
    title: 'Quantum Computing & Entanglement Principles',
    createdAt: 'Today, 2:15 PM',
    updatedAt: 'Today, 2:18 PM',
    messageCount: 3,
    status: 'active',
    tags: ['Physics', 'Quantum'],
    messages: [
      {
        id: 'msg-01',
        role: 'user',
        content: 'Explain quantum computing and how superposition works.',
        timestamp: '2:15 PM',
        status: 'complete',
      },
      {
        id: 'msg-02',
        role: 'assistant',
        content: 'Quantum computing leverages fundamental principles of quantum mechanics.',
        timestamp: '2:16 PM',
        status: 'complete',
        blocks: [
          {
            id: 'blk-01',
            type: 'text',
            content:
              'Quantum computing is a revolutionary paradigm that harnesses superposition, entanglement, and quantum interference to process information exponentially faster than binary transistors for specific computational domains.',
          },
          {
            id: 'blk-02',
            type: 'markdown',
            content:
              '### Core Quantum Concepts\n\n- **Superposition**: Qubits exist simultaneously in linear combinations of $|0\\rangle$ and $|1\\rangle$ states until measured.\n- **Entanglement**: Non-local correlations where measuring one qubit instantaneously determines the state of its entangled partner.\n- **Quantum Interference**: Constructive interference amplifies correct computational probability paths while destructive interference cancels erroneous paths.',
          },
          {
            id: 'blk-03',
            type: 'code',
            codeData: {
              language: 'python',
              filename: 'quantum_circuit.py',
              code: 'from qiskit import QuantumCircuit, Aer, execute\n\n# Create a 2-qubit Bell State circuit\ncircuit = QuantumCircuit(2, 2)\ncircuit.h(0)         # Hadamard gate on Qubit 0\ncircuit.cx(0, 1)     # CNOT gate with control 0 and target 1\ncircuit.measure([0, 1], [0, 1])\n\nsimulator = Aer.get_backend("qasm_simulator")\njob = execute(circuit, simulator, shots=1000)\nresult = job.result()\nprint("Bell State Counts:", result.get_counts())',
            },
          },
          {
            id: 'blk-04',
            type: 'table',
            tableData: {
              headers: ['Parameter', 'Classical Computer', 'Quantum Computer'],
              rows: [
                ['Fundamental Unit', 'Bit (0 or 1)', 'Qubit (|0⟩, |1⟩, or superposition)'],
                ['State Capacity', 'N bits = 1 state', 'N qubits = 2^N state vector'],
                ['Scaling Speed', 'Polynomial / Linear', 'Exponential (Shor, Grover)'],
              ],
            },
          },
          {
            id: 'blk-05',
            type: 'citation',
            citationsData: [
              {
                id: 'cit-1',
                title: 'Quantum Computation and Quantum Information',
                source: 'Nielsen & Chuang (Cambridge University Press)',
                snippet: 'Foundation textbook detailing quantum circuits and teleportation protocols.',
              },
              {
                id: 'cit-2',
                title: 'Quantum Supremacy Using a Programmable Superconducting Processor',
                source: 'Nature 574, 505–510 (2019)',
                snippet: 'Experimental demonstration of quantum speedup over classical supercomputers.',
              },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 'conv-02',
    title: 'Python Sorting Algorithm Implementation & Benchmarks',
    createdAt: 'Yesterday, 4:30 PM',
    updatedAt: 'Yesterday, 4:35 PM',
    messageCount: 2,
    status: 'active',
    tags: ['Coding', 'Algorithms'],
    messages: [
      {
        id: 'msg-03',
        role: 'user',
        content: 'Write a Python program to implement QuickSort with performance benchmarks.',
        timestamp: '4:30 PM',
        status: 'complete',
      },
      {
        id: 'msg-04',
        role: 'assistant',
        content: 'Here is an optimized Python QuickSort implementation.',
        timestamp: '4:32 PM',
        status: 'complete',
        blocks: [
          {
            id: 'blk-06',
            type: 'code',
            codeData: {
              language: 'python',
              filename: 'quicksort.py',
              code: 'def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)\n\n# Benchmark\nimport time, random\ndata = [random.randint(1, 100000) for _ in range(50000)]\nstart = time.perf_counter()\nsorted_data = quicksort(data)\nelapsed = time.perf_counter() - start\nprint(f"Sorted 50,000 items in {elapsed:.4f} seconds")',
            },
          },
        ],
      },
    ],
  },
];
