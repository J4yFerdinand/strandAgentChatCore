import { StackContext, Function, Api } from "sst/constructs";

export function API({ stack }: StackContext) {
  const apiFn = new Function(stack, "FastApiLambda", {
    runtime: "python3.12",
    handler: "lambda_handler.handler",
    srcPath: "packages/fastapi-app",
    bundle: {
      assetExcludes: ["__pycache__", "*.pyc"]
    }
  });

  const api = new Api(stack, "FastApi", {
    routes: {
      "GET /": apiFn,
      "GET /hello": apiFn,
      "POST /data": apiFn
    }
  });

  stack.addOutputs({
    ApiEndpoint: api.url
  });
}