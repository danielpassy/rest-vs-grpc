# rest-vs-grpc
This is an lab to study performance and devx of communicating between services with 2 protocols:
- REST
- GRCP

GRCP is suppose to have many benefits, but
- how much does it matter in terms of perf?
- How easy is it to adopt it?
- How easy is to share typing between micro services?


We implemented 2 dockerized services in this project, each one inside apps folder
- FastApi project that has no DB whatsoever, but keep create random gibberish on memory
- Go project, that exposes and API that can either be REST or GRPC that receive this random gibberish, do some random stuff and return a result


We'll build those two services, containerize both and communicate those locally.
After
We'll deploy those in as an ECS in the same vpc and we'll communicate through internal endpoints and measure it using sentry, everthing using terraform that should sit in infrastructure 


GUIDELINES:
- Simplciity over complexity
- Fail fast: add a schema validator at the entry points of the service and then the data has no variance, so we don't need to branch for random stuff
- Fail fast: if something is wrong, just let it crash
- Use UV for python
- Write mostly integration test at app level, i.e. tests that uses client to test like an http calls, but inside the framwork (e.g. django client)
- Hardcode a lot of stuff for now
- we don't need complex benchmark for now 
