<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

IF3140 Database Management, Assignment 2: Concurrency Control (Locking, OCC and MVCC).

---

## Part 1: Simple Locking (exclusive locks only)

The protocol goes like this:

1. Upon entering the system, each transaction requests an EXCLUSIVE lock on EVERY item that it will either read or write.
2. The transaction waits until the lock is granted for a set amount of time.  
   2a) If the `lock_manager` doesn't reply after TIMEOUT then the transaction is aborted
   2b) If the `lock_manager` replies before TIMEOUT then the transaction will keep track of all the locks it has acquired and proceeds with the logic of the transaction
3. Release ALL locks at commit/abort time.

There are two main components inside my implementation, a lock manager `lock_manager` and the main processor `txn_processor`. The lock manager is executed on a subprocess while the txn_processor is executed on the main process. To avoid the complexities of creating a thread-safe lock manager for this assignment, the lock manager is implemented using a single thread that manages the state of the lock manager, this single lock manager threa may become a performance bottleneck as it has to request and release locks on behalf of ALL transactions. The transactions itself is ran inside the `txn_processor` with multiple threads. The `txn_processor` and the `lock_manager` interprocess communication is handled by a pipe. Whenever any transaction needs a to request or release a lock, it sends a message through this pipe from the `txn_processor` child thread to the `lock_manager` process. `lock_manager` will queue this request inside the lock table and it will notify the `txn_processor` main thread whenever a transaction has acquired a lock. Inside the `txn_processor`, it has a message queue where every acknowledgements from the `lock_manager` are published and every child thread subscribes to this message queue and whenever they see their own thread acquires a lock, it dequeue the message from the message queue and stores its own locks inside their own thread. The same process happens for lock releases

---

## Part 2: Serial Optimistic Concurrency Control (OCC)

Three phases of transactions executed with OCC

1. Read phase
2. Validation phase
3. Write phase

When a transaction enters phase 2, the protocol validates the transaction `j` with a validation test

- if for all `Ti` with `TS(Ti) < Ts(Tj)` either one of the following condition holds:
  - `finishTS(Ti) < startTs(Tj)`
  - `startTS(Tj) < finishTS(Ti) < validationTS(Tj)` and the set of data items written by `Ti` does not intersect with the set of data items read by `Tj`
    then the validation suceeds and `Tj` can be committed

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Simple Exclusive Lock
- [x] OCC
- [x] Timeout based deadlock prevention
- [ ] MVCC
- [ ] Unimplemented
  - [ ] Cascading rollback
  - [ ] Better deadlock prevention
- [ ] Complete rewrite in C for better concurrency

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

- python 3.8

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Your Name - [@jessonyo](https://twitter.com/your_username) - aphostrophy@gmail.com

Project Link: [https://github.com/aphostrophy/database-concurrency-control](https://github.com/aphostrophy/database-concurrency-control)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

References

- [Dhatch/Database-Concurrency-Control](https://github.com/dhatch/database-concurrency-control)

<p align="right">(<a href="#top">back to top</a>)</p>
