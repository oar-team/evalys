settings.outformat = "pdf";
unitsize(1cm);
import patterns;

real point_size = 0.2;

struct Job
{
    string id = "job";
    int submission_date = 0;
    int processing_time = 1;
    int requested_time = 0;
    int number_of_requested_resources = 1;
    real starting_time = 0;
    real allocation_start = 0;
    pen fill_color = rgb(180, 180, 180);

    void operator init(string id,
                       int submission_date = 0,
                       int processing_time = 1,
                       int requested_time = 0,
                       int number_of_requested_resources = 1,
                       real starting_time = 0,
                       real allocation_start = 0,
                       pen fill_color = rgb(180, 180, 180))
    {
        this.id = id;
        this.submission_date = submission_date;
        this.processing_time = processing_time;
        this.requested_time = requested_time;
        this.number_of_requested_resources = number_of_requested_resources;
        this.starting_time = starting_time;
        this.allocation_start = allocation_start;
        this.fill_color = fill_color;
    }
}

Job job_copy(Job job)
{
    Job j;
    j.id = job.id;
    j.submission_date = job.submission_date;
    j.processing_time = job.processing_time;
    j.requested_time = job.requested_time;
    j.number_of_requested_resources = job.number_of_requested_resources;
    j.starting_time = job.starting_time;
    j.allocation_start = job.allocation_start;
    j.fill_color = job.fill_color;

    return j;
}

add("hatch",hatch());
add("hatch2",hatch(1.5mm, NE));
add("hatchback",hatch(NW));
add("brick",brick());
add("crosshatch",crosshatch(3mm));

string default_pattern = "hatch2";

void draw_job(Job j, bool draw_requested_time = false, bool draw_id = true,
              string requested_time_pattern = default_pattern)
{
    path executed_path = (j.starting_time, j.allocation_start) --
                         (j.starting_time + j.processing_time, j.allocation_start) --
                         (j.starting_time + j.processing_time, j.allocation_start + j.number_of_requested_resources) --
                         (j.starting_time, j.allocation_start + j.number_of_requested_resources) -- cycle;

    path non_executed_path = (j.starting_time + j.processing_time, j.allocation_start) --
                             (j.starting_time + j.requested_time, j.allocation_start) --
                             (j.starting_time + j.requested_time, j.allocation_start + j.number_of_requested_resources) --
                             (j.starting_time + j.processing_time, j.allocation_start + j.number_of_requested_resources) --
                             (j.starting_time + j.processing_time, j.allocation_start) -- cycle;

    filldraw(executed_path, j.fill_color, black);

    if (draw_id)
    {
        pair id_loc = (j.starting_time, j.allocation_start) +
                      (j.processing_time, j.number_of_requested_resources) / 2;
        label((string)j.id, id_loc);
    }

    if (draw_requested_time && j.requested_time > j.processing_time)
    {
        filldraw(non_executed_path, j.fill_color);
        filldraw(non_executed_path, pattern(requested_time_pattern), black);
        /*draw((j.starting_time + j.processing_time, j.allocation_start) --
             (j.starting_time + j.requested_time, j.allocation_start + j.number_of_requested_resources));
        draw((j.starting_time + j.processing_time, j.allocation_start + j.number_of_requested_resources) --
             (j.starting_time + j.requested_time, j.allocation_start));*/
    }
}

void draw_job_on_position(Job j, pair position,
                          bool draw_requested_time = false,
                          bool draw_id = true,
                          string requested_time_pattern = default_pattern,
                          bool centered = false)
{
    Job j2 = job_copy(j);

    j2.starting_time = position.x;
    j2.allocation_start = position.y;

    if (centered)
    {
        real width = j2.processing_time;
        if (draw_requested_time)
            width = max(width, j2.requested_time);

        real height = j2.number_of_requested_resources;

        j2.starting_time -= width/2;
        j2.allocation_start -= height/2;
    }

    draw_job(j2, draw_requested_time=draw_requested_time,
             draw_id=draw_id,
             requested_time_pattern=requested_time_pattern);
}

void draw_frame(real t0, real t1, real m0, real m1, real dash_width=1/8,
                bool draw_time_axe_values = true,
                bool draw_time_axe_label = true,
                bool draw_machine_axe_values = true,
                bool draw_machine_axe_label = true,
                bool draw_machines_separations = true,
                bool draw_time_axe = true,
                bool draw_machines_axe = true,
                int current_time = -1,
                bool draw_current_time = false)
{
    // Time axe
    if (draw_time_axe)
    {
        draw((t0,m0) -- (t1+2,m0), Arrow);
        if (draw_time_axe_label)
            label("$time$", (t1+2,m0), align=right);

        // Time ticks
        for (int i = (int)t0; i <= (int)t1; ++i)
        {
            draw((i,m0-dash_width) -- (i,m0), black);
            if (draw_time_axe_values)
            {
                pen p;
                if (draw_current_time && current_time == i)
                    p = red;
                label((string)i, (i,m0-dash_width), p, align=down);
            }
        }
    }

    // Machine axe
    if (draw_machines_axe)
    {
        draw((t0,m0) -- (t0, m1+1), Arrow);
        if (draw_machine_axe_label)
            label("$machines$", (t0, m1+1), align=up);

        // Machine ticks
        draw((t0-dash_width,m0) -- (t0,m0), black);

        for (int i = (int)m0+1; i <= (int)m1; ++i)
        {
            draw((t0-dash_width,i) -- (t0,i), black);
            if (draw_machine_axe_values)
                label("M"+(string)i, (t0-dash_width,i-0.5), align=left);
        }
    }

    // Machine lines
    if (draw_machines_separations)
    {
        for (int i = (int)m0+1; i <= (int)m1; ++i)
            draw((t0,i) -- (t1,i), black+linewidth(0.2)+linetype(new real[] {16,8,0,32}));
    }
}
